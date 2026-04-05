from flask import Blueprint, request, jsonify, session
from backend.app.services.quiz_service import create_quiz

quiz_bp = Blueprint('quiz', __name__)


@quiz_bp.route('/create', methods=['POST'])
def create_quiz():
    pass