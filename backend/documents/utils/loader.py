import requests
import tempfile
import os
import fitz  # PyMuPDF
import logging
from langchain.schema import Document
from typing import List

logger = logging.getLogger(__name__)

class DocumentLoader:
    @staticmethod
    def load_from_url(url: str) -> List[Document]:
        try:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                temp_file.write(response.content)
                temp_path = temp_file.name
            
            docs = DocumentLoader._load_pdf(temp_path)
            os.unlink(temp_path)
            return docs
        except Exception as e:
            logger.error(f"Failed to load from URL: {str(e)}")
            raise

    @staticmethod
    def load_from_file(file_path: str) -> List[Document]:
        return DocumentLoader._load_pdf(file_path)

    @staticmethod
    def _load_pdf(file_path: str) -> List[Document]:
        try:
            doc = fitz.open(file_path)
            docs = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text("text", sort=True)
                metadata = {"source": file_path, "page": page_num + 1}
                docs.append(Document(page_content=text, metadata=metadata))
            return docs
        except Exception as e:
            logger.error(f"PDF loading error: {str(e)}")
            raise