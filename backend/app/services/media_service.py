import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mp3', 'wav'}


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_media_file(file, upload_folder: str = None) -> dict:
    if not file or file.filename == '':
        raise ValueError("Файл не предоставлен")
    
    if not allowed_file(file.filename):
        raise ValueError(f"Недопустимое расширение файла. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}")
    
    if upload_folder is None:
        upload_folder = os.path.join(current_app.root_path, '../../../..', 'frontend', 'static', 'uploads')
    
    upload_folder = os.path.abspath(upload_folder)
    os.makedirs(upload_folder, exist_ok=True)
    
    original_filename = secure_filename(file.filename)
    ext = original_filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    
    filepath = os.path.join(upload_folder, unique_name)
    file.save(filepath)
    
    relative_path = f"/static/uploads/{unique_name}"
    
    return {
        'filename': original_filename,
        'saved_as': unique_name,
        'path': filepath,
        'url': relative_path
    }


def delete_media_file(filename: str, upload_folder: str = None) -> bool:
    if upload_folder is None:
        upload_folder = os.path.join(current_app.root_path, '../../../..', 'frontend', 'static', 'uploads')
    
    filepath = os.path.join(upload_folder, filename)
    
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


def get_media_url(filename: str) -> str:
    return f"/static/uploads/{filename}"
