from flask import render_template, current_app
from app.email import send_email


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Aisino Docker Manager] 重置密码邮件',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))


def send_registry_confirm_email(user):
    token = user.get_register_confirm_token()
    send_email('[Aisino Docker Manager] 注册确认邮件',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/register_confirm.txt',
                                         user=user, token=token),
               html_body=render_template('email/register_confirm.html',
                                         user=user, token=token))
