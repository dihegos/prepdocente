import json
from prepdocente import create_app
from prepdocente.models import db, Question

app = create_app()

with open("questions.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with app.app_context():
    inserted = 0
    updated = 0

    for q in data:
        obj = Question.query.filter_by(number=q["number"]).first()

        if obj:
            obj.category = q["category"]
            obj.prompt = q["prompt"]
            obj.option_a = q["option_a"]
            obj.option_b = q["option_b"]
            obj.option_c = q["option_c"]
            obj.option_d = q["option_d"]
            obj.correct_option = q["correct_option"]
            obj.explanation = q.get("explanation", "")
            obj.image = q.get("image")
            obj.video_url = q.get("video_url")
            updated += 1
        else:
            obj = Question(
                number=q["number"],
                category=q["category"],
                prompt=q["prompt"],
                option_a=q["option_a"],
                option_b=q["option_b"],
                option_c=q["option_c"],
                option_d=q["option_d"],
                correct_option=q["correct_option"],
                explanation=q.get("explanation", ""),
                image=q.get("image"),
                video_url=q.get("video_url"),
            )
            db.session.add(obj)
            inserted += 1

    db.session.commit()
    print(f"Insertadas: {inserted}")
    print(f"Actualizadas: {updated}")