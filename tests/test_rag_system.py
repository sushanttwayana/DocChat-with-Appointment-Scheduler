import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path to import chatbot modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chatbot.rag_system import create_vector_store, setup_rag_chain


class TestRAGSystem(unittest.TestCase):
    
    def setUp(self):
        # Create mock documents for testing
        self.mock_documents = [
            MagicMock(page_content="This is a test document about AI", metadata={"source": "test1.txt"}),
            MagicMock(page_content="RAG systems combine retrieval with generation", metadata={"source": "test2.txt"}),
            MagicMock(page_content="LangChain provides tools for building RAG applications", metadata={"source": "test3.txt"})
        ]
    
    @patch('chatbot.rag_system.Chroma')
    @patch('chatbot.rag_system.OpenAIEmbeddings')
    def test_create_vector_store(self, mock_embeddings, mock_chroma):
        # Setup mocks
        mock_embeddings_instance = MagicMock()
        mock_embeddings.return_value = mock_embeddings_instance
        
        mock_vector_store = MagicMock()
        mock_chroma.from_documents.return_value = mock_vector_store
        
        # Call the function under test
        result = create_vector_store(self.mock_documents)
        
        # Assertions
        mock_embeddings.assert_called_once()
        mock_chroma.from_documents.assert_called_once_with(self.mock_documents, mock_embeddings_instance)
        self.assertEqual(result, mock_vector_store)
    
    @patch('chatbot.rag_system.RetrievalQA')
    @patch('chatbot.rag_system.OpenAI')
    def test_setup_rag_chain(self, mock_openai, mock_retrieval_qa):
        # Setup mocks
        mock_llm = MagicMock()
        mock_openai.return_value = mock_llm
        
        mock_vector_store = MagicMock()
        mock_retriever = MagicMock()
        mock_vector_store.as_retriever.return_value = mock_retriever
        
        mock_qa_chain = MagicMock()
        mock_retrieval_qa.from_chain_type.return_value = mock_qa_chain
        
        # Call the function under test
        result = setup_rag_chain(mock_vector_store)
        
        # Assertions
        mock_openai.assert_called_once_with(temperature=0)
        mock_vector_store.as_retriever.assert_called_once_with(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        mock_retrieval_qa.from_chain_type.assert_called_once_with(
            llm=mock_llm,
            chain_type="stuff",
            retriever=mock_retriever,
            return_source_documents=True
        )
        self.assertEqual(result, mock_qa_chain)
    
    def test_query_with_rag_chain(self):
        # Create a mock RAG chain
        mock_qa_chain = MagicMock()
        mock_qa_chain.return_value = {
            "result": "This is a test answer about RAG systems.",
            "source_documents": self.mock_documents
        }
        
        # Test querying the chain
        result = mock_qa_chain({"query": "How do RAG systems work?"})
        
        # Assertions
        mock_qa_chain.assert_called_once_with({"query": "How do RAG systems work?"})
        self.assertEqual(result["result"], "This is a test answer about RAG systems.")
        self.assertEqual(result["source_documents"], self.mock_documents)


if __name__ == '__main__':
    unittest.main()