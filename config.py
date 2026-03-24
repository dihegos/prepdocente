import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-cambiar")
    SQLALCHEMY_DATABASE_URI = "sqlite:///prepdocente.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False