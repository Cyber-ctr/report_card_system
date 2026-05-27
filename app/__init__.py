import os
from flask import Flask, render_template
from .config import Config
from .extensions import db, migrate, login_manager, bcrypt, csrf, limiter
from .services import configure_security_headers, register_cli_commands
from .auth.routes import auth_bp
from .admin.routes import admin_bp
from .teacher.routes import teacher_bp
from .reports.routes import reports_bp
from .main.routes import main_bp

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(teacher_bp, url_prefix="/teacher")
    app.register_blueprint(reports_bp, url_prefix="/reports")

    configure_security_headers(app)
    register_cli_commands(app)

    @app.context_processor
    def inject_branding():
        return {
            "app_name": app.config.get("APP_NAME", "ScholaTrack"),
            "app_tagline": app.config.get("APP_TAGLINE", "Secure Academic Reporting Platform"),
        }

    with app.app_context():
        if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite") or os.getenv("AUTO_CREATE_DB", "true").lower() == "true":
            db.create_all()
            from .models import SchoolSettings
            if not SchoolSettings.query.first():
                db.session.add(SchoolSettings())
                db.session.commit()


    @app.errorhandler(404)
    def not_found(_):
        return render_template("main/error.html", title="Page not found", heading="404", message="The page you requested does not exist."), 404

    @app.errorhandler(403)
    def forbidden(_):
        return render_template("main/error.html", title="Access denied", heading="403", message="You do not have permission to access this page."), 403

    @app.errorhandler(500)
    def server_error(_):
        return render_template("main/error.html", title="Server error", heading="500", message="An unexpected error occurred. Please try again later."), 500

    return app
