from flask import render_template, request, redirect, url_for, session, flash

from . import auth_bp
from .services import register_user, authenticate_user
from .forms import RegistrationForm, LoginForm
from .utils import get_current_user

# ==================================================
# Register
# ==================================================

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    
    if get_current_user() is not None:
        print("ログイン済み")
        return redirect(url_for("mypage.index"))
    
    form = RegistrationForm()

    if form.validate_on_submit():

        user = register_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        
        if user is None:
            flash("ユーザー名またはメールアドレスが既に使用されています。")
            return render_template("auth/register.html")

        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)
  

# ==================================================
# Login
# ==================================================

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if get_current_user() is not None:
        print("ログイン済み")
        return redirect(url_for("mypage.index"))

    form = LoginForm()

    if form.validate_on_submit():

        user = authenticate_user(
            username=form.username.data,
            password=form.password.data,
        )

        if user is None:
            # ログイン失敗
            form.username.errors.append(
                "ユーザー名またはパスワードが正しくありません。"
            )

            return render_template(
                "auth/login.html",
                form=form,
            )

        # ログイン成功
        session["user_id"] = user.id
        return redirect(url_for("main.index"))

    return render_template(
        "auth/login.html",
        form=form,
    )


# ==================================================
# Logout
# ==================================================

@auth_bp.route("/logout")
def logout():

    session.pop("user_id", None)

    return redirect(url_for("main.index"))