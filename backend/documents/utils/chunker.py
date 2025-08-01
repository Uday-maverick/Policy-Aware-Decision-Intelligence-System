from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from typing import List
from django.conf import settings

class TextChunker:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            is_separator_regex=False,
            add_start_index=True
        )
    
    def chunk(self, documents: List[Document]) -> List[Document]:
        chunked_documents = []
        for doc in documents:
            chunks = self.splitter.split_documents([doc])
            for chunk in chunks:
                chunk.metadata = {
                    **doc.metadata,
                    **chunk.metadata,
                    "position": {
                        "start": chunk.metadata.get("start_index", 0),
                        "end": chunk.metadata.get("start_index", 0) + len(chunk.page_content)
                    }
                }
                chunked_documents.append(chunk)
        return chunked_documents