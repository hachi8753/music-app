from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
)


class RegistrationForm(FlaskForm):

    username = StringField(
        "ユーザー名",
        validators=[
            DataRequired(),
            Length(min=3, max=20),
        ],
    )

    email = StringField(
        "メールアドレス",
        validators=[
            DataRequired(),
            Email(),
            Length(max=255),
        ],
    )

    password = PasswordField(
        "パスワード",
        validators=[
            DataRequired(),
            Length(min=8, max=128),
        ],
    )

    password_confirm = PasswordField(
        "パスワード（確認）",
        validators=[
            DataRequired(),
            EqualTo("password"),
        ],
    )
    
    submit = SubmitField("登録")

class LoginForm(FlaskForm):
    
    username = StringField(
        "ユーザー名",
        validators=[
            DataRequired(),
            Length(min=3, max=20),
        ],
    )
    
    password = PasswordField(
        "パスワード",
        validators=[
            DataRequired(),
            Length(min=8, max=128),
        ],
    )
        
    submit = SubmitField("ログイン")