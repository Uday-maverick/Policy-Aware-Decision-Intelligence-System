import uuid
from django.db import models

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_type = models.CharField(max_length=20)  # url, file
    source_path = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source_type} - {self.source_path}"

class DocumentChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    content = models.TextField()
    embedding = models.BinaryField()  # Storing FAISS-compatible embeddings
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

class ChatHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=255, db_index=True)
    question = models.TextField()
    answer = models.TextField()
    entities = models.JSONField(default=dict)
    relevant_clauses = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    response_time = models.FloatField(default=0.0)