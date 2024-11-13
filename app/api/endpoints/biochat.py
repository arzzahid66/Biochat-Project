from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import status
from fastapi.responses import JSONResponse
import pandas as pd
import fitz 
import os   
from app.schemas.schema import QueryInput
from app.utils.utils_biochat import graph_builder_function
from app.utils.retrieval_utils import retrieval_qa , pandas_df_agent
from app.utils.lcel_chain_pinecone_class import PineconeInsertRetrieval
from pinecone import Pinecone
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")
pinecone_ar_retrieval = PineconeInsertRetrieval(pinecone_api_key)
from io import BytesIO
from fastapi import  UploadFile
from docx import Document as DocxDocument
from uuid import uuid4
biochat_router = APIRouter()
from io import BytesIO
from fastapi import UploadFile, HTTPException
from uuid import uuid4
memory_storage = {}

# ingestion
@biochat_router.post("/ingestion")
async def ingestion_file(file: UploadFile):
    graph_builder_fun = graph_builder_function()
    original_file_name = file.filename
    await file.seek(0)
    file_bytes = None
    try:
        file_extension = original_file_name.lower().split('.')[-1]
        # Handle CSV/Excel files
        if file_extension not in ["csv", "xlsx","docx","doc","pdf","txt","png","jpg","jpeg"]:
            raise ValueError("Unsupported file extension") 
        
        if file_extension in ["csv", "xlsx"]:
            file_key = f"{str(uuid4())}.{file_extension}"
            file_content = await file.read()
            memory_storage[file_key] = BytesIO(file_content)
            result = graph_builder_fun.invoke({
                "original_file_name": original_file_name,
                "excel_csv_file_key": file_key
            })
            data = {"result": result["output_result"]}
            return JSONResponse(
                {"message": "Ingestion Successful!", "data": data}, 
                status_code=status.HTTP_200_OK
            )   

        if file_extension in ["docx", "doc", "pdf", "txt"]:
            if file_extension == "docx" or file_extension == "doc":    
                file_bytes = await file.read()
                docx_bytes = BytesIO(file_bytes)
                document = DocxDocument(docx_bytes)
                text = "\n".join([para.text for para in document.paragraphs])
                file_text = text
            elif file_extension == "pdf":
                file_bytes = await file.read()
                file_bytes = BytesIO(file_bytes)
                document = fitz.open(stream=file_bytes, filetype="pdf")
                text = ""
                for page_num in range(len(document)):
                    page = document.load_page(page_num)
                    text += page.get_text()
                file_text = text
            elif file_extension == "txt":
                file_bytes = await file.read()
                file_text = file_bytes.decode("utf-8")
            else:
                raise ValueError("Unsupported file extension")  
            result = graph_builder_fun.invoke({
                "original_file_name": original_file_name,
                "file_text": file_text,
            })

            data = {"result": result["output_result"]}
            return JSONResponse(
                {"message": "Ingestion Successful!", "data": data}, 
                status_code=status.HTTP_200_OK
            )

        if file_extension in ["png", "jpg", "jpeg"]: 
            file_bytes = await file.read()
            # file_bytes = BytesIO(file_bytes)
            result = graph_builder_fun.invoke({
                "original_file_name": original_file_name,
                "image_bytes": file_bytes
            })

            data = {"result": result["output_result"]}
            return JSONResponse(
                {"message": "Ingestion Successful!", "data": data}, 
            status_code=status.HTTP_200_OK
        )
    except Exception as ex:
        return JSONResponse(
            content={"message": f"An error occurred: {str(ex)}"}, 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# qa_retrieval
@biochat_router.post("/retrieval")
async def retrieval_file(query_input: QueryInput):
    try:
        query = query_input.query
        collection_name = query_input.collection_name
        if collection_name.endswith("xlsx") or collection_name.endswith("csv"):
            if collection_name not in memory_storage:
                raise HTTPException(status_code=404, detail="File not found")
            
            file_stream = memory_storage[collection_name]
            file_stream.seek(0)  # Reset stream position if needed
            file_extension = collection_name.lower().split('.')[-1]
            if file_extension in ['xlsx','xls']:
                df = pd.read_excel(file_stream)
            elif file_extension in 'csv':
                df = pd.read_csv(file_stream)
            pamdas_agent_result = pandas_df_agent(query,df)
            return JSONResponse({"message": "Retrieval Successful!", "data": pamdas_agent_result}, status_code=status.HTTP_200_OK)
        result = retrieval_qa(query,collection_name)
        return JSONResponse({"message": "Retrieval Successful!", "data": result}, status_code=status.HTTP_200_OK)
    except Exception as ex:
        return JSONResponse(content={"message": f"An error occurred: {str(ex)}"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



# delete namespace
@biochat_router.delete("/delete_namespace/{namespace}")
async def delete_namespace(namespace: str):
    try:
        # Initialize Pinecone client
        pc = Pinecone(api_key=pinecone_api_key)
        index = pc.Index(pinecone_index_name)
        # Get list of namespaces in the index
        stats = index.describe_index_stats()
        existing_namespaces = stats.namespaces.keys()

        # Check if namespace exists
        if namespace not in existing_namespaces:
            return JSONResponse(
                content={"message": f"Namespace '{namespace}' not found in index"},
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Delete the namespace if it exists
        pinecone_ar_retrieval.delete_name_spaces(pinecone_index_name, namespace)
        
        return JSONResponse(
            content={"message": f"Namespace '{namespace}' deleted successfully"},
            status_code=status.HTTP_200_OK
        )
            
    except Exception as ex:
        return JSONResponse(
            content={"message": f"An error occurred while deleting namespace: {str(ex)}"}, 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )







# @biochat_router.post("/upload-file/")
# async def upload_file(file: UploadFile):
#     # Generate a unique key for each file upload (e.g., using UUID)
#     file_key = str(uuid4())
#     file_content = await file.read()  # Read file content
#     memory_storage[file_key] = BytesIO(file_content)  # Store in BytesIO

#     return {"status": "file stored in memory", "file_key": file_key}

# @biochat_router.get("/process-file/{file_key}")
# async def process_file(file_key: str):
#     # Check if the file exists in memory
#     if file_key not in memory_storage:
#         raise HTTPException(status_code=404, detail="File not found")

#     file_stream = memory_storage[file_key]
#     file_stream.seek(0)  # Reset stream position if needed
#     content = file_stream.read()  # Process file data

#     return {"content": content.decode()}




# def extract_text_from_pdf(file_data: BytesIO):
#     document = fitz.open(stream=file_data, filetype="pdf")
#     text = ""
#     for page_num in range(len(document)):
#         page = document.load_page(page_num)
#         text += page.get_text()
#     return text