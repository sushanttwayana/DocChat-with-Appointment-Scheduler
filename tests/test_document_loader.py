import pytest
import os
import tempfile
from chatbot.document_loader import load_documents

class TestDocumentLoader:
    
    def test_load_text_document(self):
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp:
            temp.write(b"This is a test document.\nIt has multiple lines.\nThis is used for testing the document loader.")
            temp_file_path = temp.name
        
        try:
            # Load the document
            documents = load_documents(temp_file_path)
            
            # Check that documents were loaded
            assert len(documents) > 0
            
            # Check content
            assert "This is a test document" in documents[0].page_content
            
        finally:
            # Clean up
            os.unlink(temp_file_path)
    
    def test_unsupported_file_type(self):
        # Create a temporary file with unsupported extension
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as temp:
            temp.write(b"Test content")
            temp_file_path = temp.name