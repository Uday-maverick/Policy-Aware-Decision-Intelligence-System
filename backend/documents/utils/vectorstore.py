import faiss
import os
import numpy as np
import logging
from typing import List, Tuple
from django.conf import settings
from .embeddings import EmbeddingModel
from documents.models import DocumentChunk

logger = logging.getLogger(__name__)

class DualVectorStore:
    def __init__(self):
        self.embedding_model = EmbeddingModel.get_instance()
        self.faiss_index = None
        self.faiss_index_path = "./vector_store/faiss_index.bin"
        self._init_faiss()

    def _init_faiss(self):
        try:
            self.faiss_index = faiss.read_index(self.faiss_index_path)
            logger.info("Loaded existing FAISS index")
        except:
            self.faiss_index = faiss.IndexFlatL2(settings.EMBEDDING_DIM)
            logger.info("Created new FAISS index")

    def save_index(self):
        os.makedirs(os.path.dirname(self.faiss_index_path), exist_ok=True)
        faiss.write_index(self.faiss_index, self.faiss_index_path)

    def add_document_chunks(self, chunks: List[DocumentChunk]):
        embeddings = np.stack([np.frombuffer(chunk.embedding, dtype=np.float32) 
                              for chunk in chunks])
        self.faiss_index.add(embeddings)
        self.save_index()

    def search(self, query: str, k: int=5) -> List[Tuple[DocumentChunk, float]]:
        query_embedding = self.embedding_model.embed(query)
        distances, indices = self.faiss_index.search(np.array([query_embedding]), k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx >= 0:
                try:
                    chunk = DocumentChunk.objects.get(pk=idx)
                    results.append((chunk, float(distance)))
                except DocumentChunk.DoesNotExist:
                    continue
        return results