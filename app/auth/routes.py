from flask import Blueprint, flash, redirect, render_template, url_for, request
from flask_login import login_user, logout_user, login_required, current_user

from ..extensions import limiter, db
from ..models import User
from ..services import log_action
from .forms import LoginForm, PasswordChangeForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data) and user.is_active_account:
            login_user(user, remember=form.remember_me.data)
            log_action(user.id, "login", ip_address=request.remote_addr)
            flash("Welcome back.", "success")
            return redirect(url_for("main.dashboard"))
        flash("Invalid credentials or inactive account.", "danger")
    return render_template("auth/login.html", form=form, title="Login")

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    log_action(current_user.id, "logout", ip_address=request.remote_addr)
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))

@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Current password is incorrect.", "danger")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            log_action(current_user.id, "change_password", "User", current_user.id, "Password changed", request.remote_addr)
            flash("Password updated.", "success")
            return redirect(url_for("auth.profile"))
    return render_template("auth/profile.html", form=form, title="Profile")
