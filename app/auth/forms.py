from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我', default=False)
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField('密码确认', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if email.data[email.data.rindex('@'):] == 'aisino.com':
            raise ValidationError('必须使用公司邮箱注册!')
        if user is not None:
            raise ValidationError('邮箱地址太受欢迎，请输入新邮箱地址')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('发送请求')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField('密码确认', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('重置')
