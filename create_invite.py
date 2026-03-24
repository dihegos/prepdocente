from prepdocente import create_app
from prepdocente.models import db, InviteCode

app = create_app()

with app.app_context():
    code_text = "INVITADO-2026-01"

    existing = InviteCode.query.filter_by(code=code_text).first()
    if existing:
        print("Ese código ya existe.")
    else:
        invite = InviteCode(code=code_text, is_active=True)
        db.session.add(invite)
        db.session.commit()
        print(f"Código creado: {code_text}")
