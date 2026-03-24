from collections import defaultdict
from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    abort,
    flash,
)
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
)

from .models import db, User, InviteCode, Question, Attempt, Answer
from .utils import category_ranges

main_bp = Blueprint("main", __name__)

PASSING_GRADE = 8.0


def get_current_exam_set():
    return 1


def calculate_grade_10(score, total_questions):
    if not total_questions:
        return 0.0
    return round((score / total_questions) * 10, 1)


def get_questions_for_exam_set(quiz_set=1):
    return Question.query.order_by(Question.number.asc()).all()


def get_questions_for_category(category_name):
    return (
        Question.query
        .filter(Question.category == category_name)
        .order_by(Question.number.asc())
        .all()
    )


def build_category_stats_from_attempts(attempts):
    category_map = defaultdict(lambda: {"correct": 0, "total": 0})

    for attempt in attempts:
        for ans in attempt.answers:
            cat = ans.question.category if ans.question and ans.question.category else "Sin categoría"
            category_map[cat]["total"] += 1
            if ans.is_correct:
                category_map[cat]["correct"] += 1

    category_stats = []
    for name, data in category_map.items():
        total = data["total"]
        correct = data["correct"]
        accuracy = round((correct / total) * 100) if total else 0

        category_stats.append({
            "name": name,
            "correct": correct,
            "total": total,
            "accuracy": accuracy,
        })

    category_stats.sort(key=lambda x: x["accuracy"], reverse=True)
    return category_stats


@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        invite_code_text = request.form.get("invite_code", "").strip()

        if not username or not password or not confirm_password or not invite_code_text:
            flash("Completa todos los campos obligatorios.", "danger")
            return redirect(url_for("main.register"))

        if password != confirm_password:
            flash("Las contraseñas no coinciden.", "danger")
            return redirect(url_for("main.register"))

        if len(password) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.", "danger")
            return redirect(url_for("main.register"))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Ese nombre de usuario ya existe.", "danger")
            return redirect(url_for("main.register"))

        if email:
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                flash("Ese correo ya está registrado.", "danger")
                return redirect(url_for("main.register"))

        invite_code = InviteCode.query.filter_by(code=invite_code_text).first()
        if not invite_code or not invite_code.is_active or invite_code.used_by_user_id is not None:
            flash("El código de invitación no es válido o ya fue usado.", "danger")
            return redirect(url_for("main.register"))

        user = User(
            username=username,
            email=email if email else None,
        )
        user.set_password(password)

        db.session.add(user)
        db.session.flush()

        invite_code.used_by_user_id = user.id
        invite_code.used_at = datetime.utcnow()
        invite_code.is_active = False

        db.session.commit()

        login_user(user)
        flash("Cuenta creada correctamente. Bienvenido.", "success")
        return redirect(url_for("main.index"))

    return render_template("register.html")


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Sesión iniciada correctamente.", "success")
            return redirect(url_for("main.index"))

        flash("Usuario o contraseña incorrectos.", "danger")
        return redirect(url_for("main.login"))

    return render_template("login.html")


@main_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("main.login"))


@main_bp.route("/")
@login_required
def index():
    categories = category_ranges()
    current_exam_set = get_current_exam_set()

    total_questions = Question.query.count()

    attempts = (
        Attempt.query
        .filter_by(user_id=current_user.id)
        .order_by(Attempt.started_at.desc())
        .limit(8)
        .all()
    )

    return render_template(
        "index.html",
        categories=categories,
        current_exam_set=current_exam_set,
        total_questions=total_questions,
        attempts=attempts,
    )


@main_bp.route("/quiz")
@login_required
def quiz_all():
    current_set = get_current_exam_set()
    questions = get_questions_for_exam_set(current_set)

    return render_template(
        "quiz.html",
        title="Simulacro completo",
        questions=questions,
        timed=True,
        current_set=current_set,
    )


@main_bp.route("/quiz/category/<path:category>")
@login_required
def quiz_category(category):
    questions = get_questions_for_category(category)

    if not questions:
        abort(404, description=f"No se encontraron preguntas para la categoría: {category}")

    return render_template(
        "quiz.html",
        title=category,
        questions=questions,
        timed=False,
        current_set=1,
    )


@main_bp.route("/submit", methods=["POST"])
@login_required
def submit():
    mode = request.form.get("mode", "practice").strip()
    category = request.form.get("category", "").strip()
    quiz_set_raw = request.form.get("quiz_set", "1").strip()

    try:
        quiz_set = int(quiz_set_raw)
    except ValueError:
        quiz_set = 1

    question_ids = request.form.getlist("question_ids")

    if not question_ids:
        abort(400, description="No se recibieron preguntas para evaluar.")

    valid_ids = []
    for qid in question_ids:
        try:
            valid_ids.append(int(qid))
        except ValueError:
            continue

    if not valid_ids:
        abort(400, description="Los identificadores de preguntas no son válidos.")

    questions = (
        Question.query
        .filter(Question.id.in_(valid_ids))
        .order_by(Question.number.asc())
        .all()
    )

    if not questions:
        abort(400, description="No se encontraron preguntas válidas para calificar.")

    total_questions = len(questions)
    score = 0

    attempt = Attempt(
        user_id=current_user.id,
        mode=mode,
        category=category if category else None,
        quiz_set=quiz_set,
        score=0,
        total_questions=total_questions,
        grade_10=0.0,
        passed=False,
    )
    db.session.add(attempt)
    db.session.flush()

    for q in questions:
        selected_option = request.form.get(f"question_{q.id}")
        is_correct = selected_option == q.correct_option

        if is_correct:
            score += 1

        answer = Answer(
            attempt_id=attempt.id,
            question_id=q.id,
            selected_option=selected_option,
            is_correct=is_correct,
        )
        db.session.add(answer)

    grade_10 = calculate_grade_10(score, total_questions)
    passed = grade_10 >= PASSING_GRADE

    attempt.score = score
    attempt.grade_10 = grade_10
    attempt.passed = passed

    db.session.commit()

    return redirect(url_for("main.result", attempt_id=attempt.id))


@main_bp.route("/result/<int:attempt_id>")
@login_required
def result(attempt_id):
    attempt = Attempt.query.get_or_404(attempt_id)

    if attempt.user_id != current_user.id:
        abort(403)

    next_set = None
    if attempt.mode == "exam" and attempt.passed:
        next_set = (attempt.quiz_set or 1) + 1

    return render_template(
        "result.html",
        attempt=attempt,
        next_set=next_set,
    )


@main_bp.route("/review/<int:attempt_id>")
@login_required
def review(attempt_id):
    attempt = Attempt.query.get_or_404(attempt_id)

    if attempt.user_id != current_user.id:
        abort(403)

    answers = (
        Answer.query
        .filter_by(attempt_id=attempt.id)
        .join(Question, Answer.question_id == Question.id)
        .order_by(Question.number.asc())
        .all()
    )

    return render_template(
        "review.html",
        attempt=attempt,
        answers=answers,
    )


@main_bp.route("/stats")
@login_required
def stats():
    attempts = (
        Attempt.query
        .filter_by(user_id=current_user.id)
        .order_by(Attempt.started_at.desc())
        .all()
    )

    total_attempts = len(attempts)
    passed_attempts = sum(1 for a in attempts if a.passed)

    best_grade = round(max((a.grade_10 for a in attempts), default=0), 1)
    avg_grade = round(
        sum(a.grade_10 for a in attempts) / total_attempts, 1
    ) if total_attempts else 0

    total_correct = sum(a.score for a in attempts)
    total_answered = sum(a.total_questions for a in attempts)
    total_incorrect = total_answered - total_correct

    pass_rate = round((passed_attempts / total_attempts) * 100) if total_attempts else 0
    accuracy_rate = round((total_correct / total_answered) * 100) if total_answered else 0

    last_attempt = attempts[0] if attempts else None
    recent_attempts = attempts[:10]

    category_stats = build_category_stats_from_attempts(attempts)
    best_category = category_stats[0] if category_stats else None
    weakest_category = category_stats[-1] if category_stats else None

    return render_template(
        "stats.html",
        total_attempts=total_attempts,
        passed_attempts=passed_attempts,
        best_grade=best_grade,
        avg_grade=avg_grade,
        total_correct=total_correct,
        total_incorrect=total_incorrect,
        total_answered=total_answered,
        pass_rate=pass_rate,
        accuracy_rate=accuracy_rate,
        category_stats=category_stats,
        best_category=best_category,
        weakest_category=weakest_category,
        last_attempt=last_attempt,
        recent_attempts=recent_attempts,
    )