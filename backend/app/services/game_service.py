from datetime import datetime
from backend.app.db.session import db
from backend.app.models import Quiz, Question, AnswerOption
from backend.app.models_game import GameSession, SessionParticipant, ParticipantAnswer
import openpyxl
import io


def start_session(quiz_id, author_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return {"success": False, "message": "Квиз не найден"}
    if quiz.author_id != author_id:
        return {"success": False, "message": "Нет прав"}

    active = GameSession.query.filter_by(quiz_id=quiz_id, status='active').first()
    if active:
        return {"success": False, "message": "Сессия уже запущена", "session_id": active.id}

    session = GameSession(quiz_id=quiz_id, status='waiting')
    db.session.add(session)
    db.session.commit()
    return {"success": True, "session_id": session.id, "pin": quiz.pin_code}


def get_session_by_pin(pin):
    quiz = Quiz.query.filter_by(pin_code=pin).first()
    if not quiz:
        return None
    return GameSession.query.filter_by(quiz_id=quiz.id).filter(
        GameSession.status.in_(['waiting', 'active'])
    ).order_by(GameSession.id.desc()).first()


def join_session(pin, name):
    session = get_session_by_pin(pin)
    if not session:
        return {"success": False, "message": "Игра не найдена"}
    if session.status == 'finished':
        return {"success": False, "message": "Игра уже завершена"}

    existing = SessionParticipant.query.filter_by(session_id=session.id, name=name).first()
    if existing:
        return {"success": True, "participant_id": existing.id, "session_id": session.id}

    p = SessionParticipant(session_id=session.id, name=name)
    db.session.add(p)
    db.session.commit()
    return {"success": True, "participant_id": p.id, "session_id": session.id}


def next_question(session_id, author_id):
    session = GameSession.query.get(session_id)
    if not session:
        return {"success": False, "message": "Сессия не найдена"}
    if session.quiz.author_id != author_id:
        return {"success": False, "message": "Нет прав"}

    total = len(session.quiz.questions)

    if session.status == 'waiting':
        session.status = 'active'
        session.current_question_index = 0
        session.started_at = datetime.datetime.now(datetime.UTC)
    elif session.current_question_index + 1 >= total:
        session.status = 'finished'
        session.finished_at = datetime.datetime.now(datetime.UTC)
        db.session.commit()
        return {"success": True, "finished": True}
    else:
        session.current_question_index += 1

    db.session.commit()
    return {"success": True, "finished": False, "index": session.current_question_index}


def get_game_status(pin, participant_id=None):
    session = get_session_by_pin(pin)
    if not session:
        return {"success": False, "message": "Не найдено"}

    quiz = session.quiz
    result = {
        "success": True,
        "status": session.status,
        "session_id": session.id,
        "quiz_title": quiz.title,
        "total_questions": len(quiz.questions),
        "current_index": session.current_question_index,
        "participants_count": len(session.participants),
    }

    if session.status == 'active':
        questions = sorted(quiz.questions, key=lambda q: q.id)
        q = questions[session.current_question_index]
        result["question"] = {
            "id": q.id,
            "text": q.text,
            "type": q.question_type,
            "media_url": q.media_url,
            "answers": [{"id": a.id, "text": a.text} for a in q.answers]
        }

        if participant_id:
            already = ParticipantAnswer.query.filter_by(
                participant_id=participant_id, question_id=q.id
            ).first()
            result["already_answered"] = already is not None

    if session.status == 'finished':
        result["leaderboard"] = get_leaderboard(session.id)

    return result


def submit_answer(participant_id, question_id, answer_option_id=None, text_answer=None):
    participant = SessionParticipant.query.get(participant_id)
    if not participant:
        return {"success": False, "message": "Участник не найден"}

    existing = ParticipantAnswer.query.filter_by(
        participant_id=participant_id, question_id=question_id
    ).first()
    if existing:
        return {"success": False, "message": "Уже отвечено"}

    is_correct = False
    if answer_option_id:
        option = AnswerOption.query.get(answer_option_id)
        if option:
            is_correct = option.is_correct

    answer = ParticipantAnswer(
        participant_id=participant_id,
        question_id=question_id,
        answer_option_id=answer_option_id,
        text_answer=text_answer,
        is_correct=is_correct
    )
    db.session.add(answer)

    if is_correct:
        participant.score += 100

    db.session.commit()
    return {"success": True, "is_correct": is_correct, "score": participant.score}


def get_leaderboard(session_id):
    participants = SessionParticipant.query.filter_by(session_id=session_id)\
        .order_by(SessionParticipant.score.desc()).all()
    return [{"name": p.name, "score": p.score} for p in participants]


def get_question_stats(session_id, question_id):
    answers = ParticipantAnswer.query.filter_by(question_id=question_id).join(
        SessionParticipant
    ).filter(SessionParticipant.session_id == session_id).all()

    stats = {}
    for a in answers:
        if a.answer_option_id:
            option = AnswerOption.query.get(a.answer_option_id)
            key = option.text if option else "?"
            stats[key] = stats.get(key, 0) + 1

    return {"total": len(answers), "distribution": stats}


def export_results_xlsx(session_id):
    session = GameSession.query.get(session_id)
    if not session:
        return None

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Результаты"
    ws.append(["Участник", "Очки", "Правильных ответов"])

    for p in sorted(session.participants, key=lambda x: x.score, reverse=True):
        correct = sum(1 for a in p.answers if a.is_correct)
        ws.append([p.name, p.score, correct])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
