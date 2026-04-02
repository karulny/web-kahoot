import random
from app.db.session import db
from app.models import Quiz

def generate_unique_pin():
    return str(random.randint(1000, 9999))

def create_quiz_logic(title, author_id):
    new_pin = generate_unique_pin()
    new_quiz = Quiz(title=title, pin_code=new_pin, author_id=author_id)
    db.session.add(new_quiz)    
    db.session.commit()
    return new_quiz