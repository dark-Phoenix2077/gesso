from flask import Flask, render_template
from flask_migrate import Migrate
from flask_login import login_required, current_user

from config import Config
from models import db
from auth import auth_bp, init_auth

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app, db)

    init_auth(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/dashboard")
    @login_required
    def dashboard():
        return render_template("dashboard.html", user=current_user)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)