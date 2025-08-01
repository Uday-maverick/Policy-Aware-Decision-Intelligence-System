from django.urls import path
from .views import index, upload_view, chat_view, ingest_document, chat, chat_history

urlpatterns = [
    path('', index, name='index'),
    path('upload/', upload_view, name='upload'),
    path('chat/', chat_view, name='chat-view'),
    path('api/ingest/', ingest_document, name='ingest'),
    path('api/chat/', chat, name='chat'),
    path('api/history/', chat_history, name='history'),
]