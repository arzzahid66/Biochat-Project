import os
from langchain_openai import ChatOpenAI
from langchain.agents import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from app.utils.lcel_chain_pinecone_class import PineconeInsertRetrieval,SimpleQAChains
from langchain_openai import OpenAIEmbeddings
pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
model = ChatOpenAI(model="gpt-4o-mini")

lcel_qa_chain = SimpleQAChains(model)
pinecone_ar_retrieval = PineconeInsertRetrieval(api_key=pinecone_api_key)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# pandas df agent
def pandas_df_agent(query,df):
    try:  
        # print(file_path)
        # file_extension = os.path.splitext(file_path)[1].lower()
        
        # if not query or not file_path:
        #     raise ValueError("Missing required state fields: query and file_name must be provided")

        # if file_extension == '.csv':
        #     df = pd.read_csv(file_path)
        # elif file_extension == '.xlsx':
        #     try:
        #         df = pd.read_excel(file_path, engine='openpyxl')
        #     except Exception as e:
        #         raise ValueError(f"Error reading .xlsx file: {str(e)}")
        # elif file_extension == '.xls':
        #     try:
        #         df = pd.read_excel(file_path, engine='xlrd')
        #     except Exception as e:
        #         raise ValueError(f"Error reading .xls file: {str(e)}")
        # else:
        #     raise ValueError(f"Unsupported file extension: {file_extension}")

        llm = ChatOpenAI(temperature=0, model="gpt-4o-mini", streaming=True, openai_api_key=os.environ.get('OPENAI_API_KEY'))
        pandas_df_agent = create_pandas_dataframe_agent(
            llm,
            df,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            allow_dangerous_code=True,
        )

        prompt = f"""
        You are an expert Python and pandas user. You are given the following data:
        {df.head().to_string(index=False)}

        Answer the user's query below, performing any necessary calculations or analysis on the data.
        Query: {query}

        Please provide concise output, focusing on key values (like totals, averages, or other summaries), and return the results in plain text format, not code.
        """
        response = pandas_df_agent.run(prompt)
        return response

    except Exception as ex:
        return {"error": f"An error occurred: {str(ex)}"}
    

# retrieval qa
def retrieval_qa(query,collection_name):
    vectordb = pinecone_ar_retrieval.retrieve_from_namespace(index_name=pinecone_index_name,embeddings=embeddings,name_space=collection_name)
    template = """
    You are a helpful assistant. Answer the user's query based on the provided {CONTEXT}.
    Question: {question}
    """ 
    result = lcel_qa_chain.QA_Retrieval(query, template,vectordb, k=5)
    return result
