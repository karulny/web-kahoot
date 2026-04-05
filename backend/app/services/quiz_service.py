from backend.app.db.session import db
from backend.app.models import Quiz, Question, AnswerOption


def create_quiz(title, pin_code, author_id, questions_and_answers):
    try:
        quiz = Quiz(title=title, pin_code=pin_code, author_id=author_id)
        db.session.add(quiz)
        db.session.flush()

        for question in questions_and_answers["questions"]:
            new_question = Question(text=question['text'], question_type=question['question_type'],
                                    media_url=question['media_url'], quiz_id=quiz.id)
            db.session.add(new_question)
            db.session.flush()

            for answer in question['answers']:
                new_answer = AnswerOption(text=answer['text'], option_type=answer['is_correct'],
                                          question_id=new_question.id)
                db.session.add(new_answer)

        db.session.commit()
        return {"success": True, "quiz_id": quiz.id}

    except Exception as e:
        return {"success": False, "message": str(e)}