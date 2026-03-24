from prepdocente import create_app
from prepdocente.models import db, Question

app = create_app()

sample_questions = [
    {
        "number": 1,
        "category": "Matemática y razonamiento",
        "prompt": "Si un docente revisa 5 exámenes por hora, ¿cuántos revisa en 6 horas?",
        "option_a": "25",
        "option_b": "30",
        "option_c": "35",
        "option_d": "40",
        "correct_option": "B",
        "explanation": "5 × 6 = 30.",
    },
    {
        "number": 81,
        "category": "Prueba pedagógica",
        "prompt": "¿Qué enfoque promueve la construcción activa del conocimiento por parte del estudiante?",
        "option_a": "Conductismo",
        "option_b": "Memorización mecánica",
        "option_c": "Constructivismo",
        "option_d": "Castigo positivo",
        "correct_option": "C",
        "explanation": "El constructivismo plantea que el estudiante construye activamente su aprendizaje.",
    },
]

with app.app_context():
    db.create_all()
    if Question.query.count() == 0:
        for item in sample_questions:
            db.session.add(Question(**item))
        db.session.commit()
        print("Preguntas de ejemplo insertadas.")
    else:
        print("La base ya tiene preguntas.")