from django.contrib import admin
from .models import Document, DocumentChunk, ChatHistory

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'source_type', 'source_path', 'uploaded_at')

@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'created_at')
    list_filter = ('document',)

@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'question', 'created_at', 'response_time')
    search_fields = ('question', 'session_id')