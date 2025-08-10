from celery import shared_task
from .models import FileUpload, ActivityLog
import os
from docx import Document
from django.core.files.storage import default_storage

@shared_task
def process_file(file_upload_id):
    try:
        file_upload = FileUpload.objects.get(id=file_upload_id)
        file_upload.status = 'processing'
        file_upload.save()
        
        file_path = file_upload.file.path
        file_extension = os.path.splitext(file_path)[1].lower()
        
        word_count = 0
        
        if file_extension == '.txt':
            with default_storage.open(file_path, 'r') as f:
                content = f.read()
                word_count = len(content.split())
                
        elif file_extension == '.docx':
            with default_storage.open(file_path, 'rb') as f:
                doc = Document(f)
                for para in doc.paragraphs:
                    word_count += len(para.text.split())
        
        file_upload.word_count = word_count
        file_upload.status = 'completed'
        file_upload.save()
        
        ActivityLog.objects.create(
            user=file_upload.user,
            action='file_processed',
            metadata={
                'filename': file_upload.filename,
                'word_count': word_count,
                'file_id': file_upload.id
            }
        )
        
        return True
        
    except Exception as e:
        file_upload.status = 'failed'
        file_upload.save()
        
        ActivityLog.objects.create(
            user=file_upload.user,
            action='file_processing_failed',
            metadata={
                'filename': file_upload.filename,
                'error': str(e),
                'file_id': file_upload.id
            }
        )
        
        return False