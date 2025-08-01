import uuid
import json
import logging
import tempfile
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render
from .models import Document, DocumentChunk, ChatHistory
from .utils.loader import DocumentLoader
from .utils.chunker import TextChunker
from .utils.vectorstore import DualVectorStore
from .utils.groq_client import GroqClient
from .utils.parser import QueryParser
from .utils.embeddings import EmbeddingModel

logger = logging.getLogger(__name__)
text_chunker = TextChunker()
vector_store = DualVectorStore()
groq_client = GroqClient()
query_parser = QueryParser()
embedding_model = EmbeddingModel.get_instance()

def index(request):
    return render(request, 'index.html')

def upload_view(request):
    return render(request, 'upload.html')

def chat_view(request):
    return render(request, 'chat.html')

@csrf_exempt
def ingest_document(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            source_type = data.get('source_type')
            source = data.get('source')
            
            if source_type == 'url':
                docs = DocumentLoader.load_from_url(source)
            else:  # file upload
                docs = DocumentLoader.load_from_file(source)
            
            chunks = text_chunker.chunk(docs)
            
            # Create document record
            document = Document.objects.create(
                source_type=source_type,
                source_path=source
            )
            
            # Process and store chunks
            document_chunks = []
            chunk_contents = [chunk.page_content for chunk in chunks]
            embeddings = embedding_model.embed_batch(chunk_contents)
            
            for i, chunk in enumerate(chunks):
                document_chunks.append(DocumentChunk(
                    document=document,
                    content=chunk.page_content,
                    embedding=embeddings[i].tobytes(),
                    metadata=chunk.metadata
                ))
            
            # Bulk create
            DocumentChunk.objects.bulk_create(document_chunks)
            
            # Add to FAISS index
            vector_store.add_document_chunks(document_chunks)
            
            return JsonResponse({
                "status": "success",
                "document_id": str(document.id),
                "chunks": len(chunks)
            })
        except Exception as e:
            logger.error(f"Ingestion error: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid method"}, status=400)

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question')
            session_id = data.get('session_id', str(uuid.uuid4()))
            
            # Get relevant context
            context_results = vector_store.search(question, 7)
            context = "\n\n".join([
                f"Document: {chunk.document.source_path}\n"
                f"Page: {chunk.metadata.get('page', 'N/A')}\n"
                f"Content: {chunk.content}" 
                for chunk, _ in context_results
            ])
            
            # Generate answer
            response = groq_client.generate_response(context, question)
            
            # Extract entities
            entities = query_parser.parse(question)
            
            # Save to history
            ChatHistory.objects.create(
                session_id=session_id,
                question=question,
                answer=response['answer'],
                entities=entities,
                relevant_clauses=response.get('relevant_clauses', []),
                response_time=response['response_time']
            )
            
            return JsonResponse({
                "answer": response['answer'],
                "relevant_clauses": response.get('relevant_clauses', []),
                "entities": entities,
                "response_time": response['response_time'],
                "session_id": session_id
            })
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid method"}, status=400)

@csrf_exempt
def chat_history(request):
    if request.method == 'GET':
        session_id = request.GET.get('session_id')
        if not session_id:
            return JsonResponse({"error": "session_id required"}, status=400)
        
        history = ChatHistory.objects.filter(session_id=session_id).order_by('created_at')
        history_data = [{
            "question": h.question,
            "answer": h.answer,
            "entities": h.entities,
            "response_time": h.response_time,
            "timestamp": h.created_at.isoformat()
        } for h in history]
        
        return JsonResponse({"history": history_data})
    
    return JsonResponse({"error": "Invalid method"}, status=400)