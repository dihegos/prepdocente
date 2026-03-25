import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:

    # -------------------------
    # SECRET
    # -------------------------
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-cambiar"
    )

    # -------------------------
    # DATABASE URL
    # -------------------------
    db_url = os.environ.get("DATABASE_URL")

    if db_url:
        # Fix postgres:// → postgresql://
        SQLALCHEMY_DATABASE_URI = db_url.replace(
            "postgres://",
            "postgresql://",
            1
        )
    else:
        SQLALCHEMY_DATABASE_URI = (
            "sqlite:///" +
            os.path.join(BASE_DIR, "prepdocente.db")
        )

    # -------------------------
    # SQLAlchemy
    # -------------------------
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 🔥 MUY IMPORTANTE para Render / Postgres / SSL
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 5,
        "max_overflow": 2,
    }
