import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-cambiar")

    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        SQLALCHEMY_DATABASE_URI = db_url.replace("postgres://", "postgresql://", 1)
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "prepdocente.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
