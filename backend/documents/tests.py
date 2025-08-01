from django.test import TestCase
from django.urls import reverse
from .models import Document

class DocumentTests(TestCase):
    def test_document_creation(self):
        doc = Document.objects.create(
            source_type='file',
            source_path='/test/path.pdf'
        )
        self.assertEqual(str(doc), str(doc.id))
        self.assertEqual(doc.source_type, 'file')
        self.assertEqual(doc.source_path, '/test/path.pdf')