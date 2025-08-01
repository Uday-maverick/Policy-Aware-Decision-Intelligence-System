import numpy as np
import logging
from sentence_transformers import SentenceTransformer
from django.conf import settings

logger = logging.getLogger(__name__)

class EmbeddingModel:
    _instance = None
    
    def __init__(self):
        self.model = SentenceTransformer(
            settings.EMBEDDING_MODEL,
            device='cuda' if settings.USE_GPU else 'cpu'
        )
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = EmbeddingModel()
        return cls._instance

    def embed(self, text: str) -> np.ndarray:
        return self.model.encode(text, normalize_embeddings=True)
    
    def embed_batch(self, texts: list) -> np.ndarray:
        return self.model.encode(texts, batch_size=32, normalize_embeddings=True)