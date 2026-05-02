import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mp3', 'wav'}


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _get_upload_folder(upload_folder: str = None) -> str:
    if upload_folder:
        return os.path.abspath(upload_folder)
    # current_app.root_path = .../backend
    # поднимаемся на уровень выше и идём во frontend/static/uploads
    base = os.path.dirname(current_app.root_path)
    return os.path.abspath(os.path.join(base, 'frontend', 'static', 'uploads'))


def save_media_file(file, upload_folder: str = None) -> dict:
    if not file or file.filename == '':
        raise ValueError("Файл не предоставлен")

    if not allowed_file(file.filename):
        raise ValueError(
            f"Недопустимое расширение файла. Разрешены: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    folder = _get_upload_folder(upload_folder)
    os.makedirs(folder, exist_ok=True)

    original_filename = secure_filename(file.filename)
    ext = original_filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    filepath = os.path.join(folder, unique_name)
    file.save(filepath)

    return {
        'filename': original_filename,
        'saved_as': unique_name,
        'path': filepath,
        'url': f"/static/uploads/{unique_name}"
    }


def delete_media_file(filename: str, upload_folder: str = None) -> bool:
    folder = _get_upload_folder(upload_folder)
    filepath = os.path.join(folder, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


def get_media_url(filename: str) -> str:
    return f"/static/uploads/{filename}"
