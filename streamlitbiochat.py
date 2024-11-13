import streamlit as st
import requests

# Define the FastAPI base URL
BASE_URL = "http://localhost:9090"  # Change this to the actual IP address if needed

# Streamlit app
st.set_page_config(page_title="BioChat Bot", layout="wide")
st.title("BioChat Bot")
# Sidebar for file upload and management
st.sidebar.header("File Management")
# Upload file section
uploaded_file = st.sidebar.file_uploader("Upload a file", type=["csv", "xlsx", "docx", "doc", "pdf", "png", "jpg", "jpeg", "txt"])

if uploaded_file is not None:
    if st.sidebar.button("Process File"):
        # Send file to FastAPI for processing
        files = {"file": uploaded_file}
        try:
            response = requests.post(f"{BASE_URL}/query", files=files)
            response.raise_for_status()  # Raise an error for bad responses
            st.sidebar.success("File processed successfully!")
            namespace = response.json().get("data")
            st.session_state['namespace'] = namespace
        except requests.exceptions.RequestException as e:
            st.sidebar.error(f"Failed to process file: {e}")

# Cleanup section
if st.sidebar.button("Cleanup Temporary Files"):
    try:
        response = requests.delete(f"{BASE_URL}/cleanup")
        response.raise_for_status()
        st.sidebar.success("Cleanup successful!")
    except requests.exceptions.RequestException as e:
        st.sidebar.error(f"Cleanup failed: {e}")

# Delete namespace section
namespace_to_delete = st.sidebar.text_input("Namespace to delete:")
if st.sidebar.button("Delete Namespace"):
    try:
        response = requests.delete(f"{BASE_URL}/delete_namespace/{namespace_to_delete}")
        response.raise_for_status()
        st.sidebar.success(f"Namespace {namespace_to_delete} deleted successfully!")
    except requests.exceptions.RequestException as e:
        st.sidebar.error(f"Failed to delete namespace: {e}")

# Main chat interface
st.header("Chat Interface")

# Chat input without button
query = st.text_input("Enter your query:", key="chat_input")

# Automatically retrieve answer when query is entered
if query and 'namespace' in st.session_state:
    query_input = {"query": query, "collection_name": st.session_state['namespace']}
    try:
        response = requests.post(f"{BASE_URL}/retrieval", json=query_input)
        response.raise_for_status()
        answer = response.json().get("data")
        st.write("Answer:", answer)
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to retrieve answer: {e}")
elif query:
    st.warning("Please process a file first to generate a namespace.")