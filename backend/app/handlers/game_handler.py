from flask import Blueprint, request, jsonify, send_file
from backend.app.middlwares.auth import login_required
from backend.app.services.game_service import (
    start_session, join_session, next_question,
    get_game_status, submit_answer, get_leaderboard,
    get_question_stats, export_results_xlsx
)

game_bp = Blueprint('game', __name__)


@game_bp.route('/start/<int:quiz_id>', methods=['POST'])
@login_required
def start(quiz_id):
    result = start_session(quiz_id, request.user_id)
    return jsonify(result), 200 if result['success'] else 400


@game_bp.route('/join', methods=['POST'])
def join():
    data = request.get_json() or {}
    pin = data.get('pin', '').strip().upper()
    name = data.get('name', '').strip()
    if not pin or not name:
        return jsonify({"success": False, "message": "Укажите PIN и имя"}), 400
    result = join_session(pin, name)
    return jsonify(result), 200 if result['success'] else 400


@game_bp.route('/next/<int:session_id>', methods=['POST'])
@login_required
def next_q(session_id):
    result = next_question(session_id, request.user_id)
    return jsonify(result), 200 if result['success'] else 400


@game_bp.route('/status/<pin>', methods=['GET'])
def status(pin):
    # GET-запрос — participant_id передаётся как query param: /game/status/ABC?participant_id=5
    p_id = request.args.get('participant_id')
    result = get_game_status(pin, p_id)
    return jsonify(result), 200 if result['success'] else 404


@game_bp.route('/answer', methods=['POST'])
def answer():
    data = request.get_json() or {}
    p_id = data.get('participant_id')
    if not p_id:
        return jsonify({"success": False, "message": "Не в игре"}), 401

    result = submit_answer(
        participant_id=p_id,
        question_id=data.get('question_id'),
        answer_option_id=data.get('answer_option_id'),
        text_answer=data.get('text_answer')
    )
    return jsonify(result), 200 if result['success'] else 400


@game_bp.route('/stats/<int:session_id>/<int:question_id>', methods=['GET'])
@login_required
def stats(session_id, question_id):
    return jsonify(get_question_stats(session_id, question_id)), 200


@game_bp.route('/leaderboard/<int:session_id>', methods=['GET'])
def leaderboard(session_id):
    return jsonify({"success": True, "leaderboard": get_leaderboard(session_id)}), 200


@game_bp.route('/export/<int:session_id>', methods=['GET'])
@login_required
def export(session_id):
    buf = export_results_xlsx(session_id)
    if not buf:
        return jsonify({"success": False, "message": "Не найдено"}), 404
    return send_file(buf, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name=f'results_{session_id}.xlsx')