from flask import Flask
from .config import Config
from .extensions import db, migrate, login_manager, bcrypt, csrf
from .auth.routes import auth_bp
from .admin.routes import admin_bp
from .teacher.routes import teacher_bp
from .reports.routes import reports_bp
from .main.routes import main_bp
from .models import User

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(teacher_bp, url_prefix="/teacher")
    app.register_blueprint(reports_bp, url_prefix="/reports")

    @app.cli.command("create-admin")
    def create_admin():
        from getpass import getpass
        from .extensions import db
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        password = getpass("Password: ")
        if not username or not email or not password:
            print("All fields are required.")
            return
        if User.query.filter((User.username == username) | (User.email == email)).first():
            print("A user with that username or email already exists.")
            return
        user = User(username=username, email=email, role="admin", is_active=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print("Admin user created successfully.")

    return app
