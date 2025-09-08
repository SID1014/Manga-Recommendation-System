from flask import Flask
from .database import init_db
from .routes import main
from .auth_routes import auth

def create_app():
    app = Flask(__name__, static_folder="../static", template_folder="../templates")
    app.secret_key = "supersecretkey"  # change later
    init_db(app)

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix="/auth")

    return app
