from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
import tempfile
import os

def create_vector_store(documents, persist_directory=None):
    """
    Create a vector store from documents
    
    Args:
        documents (list): List of document chunks
        persist_directory (str, optional): Directory to persist the vector store
        
    Returns:
        Chroma: Vector store instance
    """
    # Create a temporary directory if none provided
    if persist_directory is None:
        persist_directory = tempfile.mkdtemp()
    
    # Initialize embeddings - can be swapped with other embedding models
    embeddings = OpenAIEmbeddings()  # Could use HuggingFaceEmbeddings for local option
    
    # Create vector store
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    # Persist the vector store
    vector_store.persist()
    
    print(f"Created vector store with {len(documents)} documents at {persist_directory}")
    
    return vector_store

def setup_rag_chain(vector_store, llm):
    """
    Set up a retrieval QA chain with the vector store
    
    Args:
        vector_store (Chroma): Vector store instance
        llm: Language model instance
        
    Returns:
        RetrievalQA: QA chain instance
    """
    # Set up retriever
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}  # Retrieve top 4 chunks
    )
    
    # Set up QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # Other options: "map_reduce", "refine"
        retriever=retriever,
        return_source_documents=True
    )
    
    return qa_chain