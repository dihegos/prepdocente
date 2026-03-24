from flask import Flask
from flask_login import LoginManager
from .models import db, User
from .routes import main_bp
from .utils import youtube_embed_url
from config import Config

login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message = "Debes iniciar sesión para continuar."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    app.jinja_env.filters["youtube_embed_url"] = youtube_embed_url

    app.register_blueprint(main_bp)
    return app