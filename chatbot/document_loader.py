import os
from langchain.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_documents(file_path):
    """
    Load documents from various file types and split into chunks
    
    Args:
        file_path (str): Path to the document or directory
        
    Returns:
        list: List of document chunks
    """
    # Determine the document type and use appropriate loader
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.txt'):
        loader = TextLoader(file_path)
    elif os.path.isdir(file_path):
        loader = DirectoryLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")
    
    # Load the documents
    documents = loader.load()
    
    if not documents:
        raise ValueError(f"No content found in the document: {file_path}")
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    
    split_docs = text_splitter.split_documents(documents)
    
    print(f"Loaded {len(documents)} document(s) and split into {len(split_docs)} chunks")
    
    return split_docs