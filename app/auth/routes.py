from flask import Blueprint, flash, redirect, render_template, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from .forms import LoginForm
from ..models import User
from ..services import log_action

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.check_password(form.password.data) and user.is_active_account:
            login_user(user)
            log_action(user.id, "login", ip_address=request.remote_addr)
            flash("Logged in successfully.", "success")
            return redirect(url_for("main.dashboard"))
        flash("Invalid credentials or inactive account.", "danger")
    return render_template("auth/login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    log_action(getattr(request, "user_id", None), "logout", ip_address=request.remote_addr)
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))
