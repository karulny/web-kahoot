from flask import Blueprint, request, jsonify
from backend.app.middlwares.auth import login_required
from backend.app.services.media_service import save_media_file, delete_media_file

media_bp = Blueprint('media', __name__)


@media_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "Файл не найден"}), 400

    file = request.files['file']
    try:
        result = save_media_file(file)
        return jsonify({"success": True, "url": result['url']}), 200
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": "Ошибка сервера"}), 500


@media_bp.route('/delete', methods=['DELETE'])
@login_required
def delete():
    data = request.get_json() or {}
    filename = data.get('filename', '').strip()
    if not filename:
        return jsonify({"success": False, "message": "Укажи имя файла"}), 400

    deleted = delete_media_file(filename)
    return jsonify({"success": deleted}), 200 if deleted else 404