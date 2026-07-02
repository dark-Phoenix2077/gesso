from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User

auth_bp = Blueprint("auth", __name__)
login_manager = LoginManager()
oauth = OAuth()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_auth(app):
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)
    oauth.init_app(app)

    # Example Google provider – you can hook this up later
    oauth.register(
        name="google",
        client_id=app.config["OAUTH_CLIENT_ID"],
        client_secret=app.config["OAUTH_CLIENT_SECRET"],
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email_or_username = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")

        user = (
            User.query.filter_by(email=email_or_username).first()
            or User.query.filter_by(username=email_or_username).first()
        )

        if user and user.passwordHash and check_password_hash(user.passwordHash, password):
            if user.isBanned:
                flash("Account banned. Contact support.", "danger")
                return redirect(url_for("auth.login"))
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid credentials.", "danger")
    return render_template("login.html")

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not email or not username or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("auth.signup"))

        if User.query.filter((User.email == email) | (User.username == username)).first():
            flash("Email or username already exists.", "danger")
            return redirect(url_for("auth.signup"))

        hashed = generate_password_hash(password)
        user = User(email=email, username=username, passwordHash=hashed)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for("dashboard"))

    return render_template("signup.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@auth_bp.route("/login/google")
def login_google():
    redirect_uri = url_for("auth.login_google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route("/login/google/callback")
def login_google_callback():
    token = oauth.google.authorize_access_token()
    userinfo = token.get("userinfo")
    if not userinfo:
        flash("Google login failed.", "danger")
        return redirect(url_for("auth.login"))

    email = userinfo["email"].lower()
    user = User.query.filter_by(email=email).first()

    if not user:
        # Create a new user with OAuth
        user = User(
            email=email,
            username=userinfo.get("given_name") or email.split("@")[0],
            displayName=userinfo.get("name"),
            avatarUrl=userinfo.get("picture"),
        )
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for("dashboard"))