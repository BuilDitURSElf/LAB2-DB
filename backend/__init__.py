from flask import Flask, jsonify, redirect
from flask_session import Session

from backend.config import Config, FRONTEND_ROOT
from backend.routes.auth import auth_bp
from backend.routes.system import system_bp
from backend.routes.todos import todos_bp


def create_app(config_class=Config):
    app = Flask(__name__, static_folder=str(FRONTEND_ROOT), static_url_path="")
    app.config.from_object(config_class)
    Session(app)
    app.register_blueprint(system_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(todos_bp)

    @app.get("/")
    def home():
        return redirect("/login.html")

    @app.errorhandler(500)
    def internal_error(_error):
        return jsonify({"error": "Internal server error"}), 500

    return app