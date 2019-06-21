from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField, PasswordField, SelectField, RadioField
from wtforms.validators import EqualTo


class UpdateUserForm(FlaskForm):
    email = StringField('Email')
    password = PasswordField('密码')
    password2 = PasswordField('密码确认', validators=[EqualTo('password')])
    role = SelectField('角色', choices=[(2, '组管理员'), (3, '普通用户')], coerce=int)
    groups = SelectMultipleField('组', coerce=int)
    image_permission = RadioField('Image', coerce=int)
    container_permission = RadioField('Container', coerce=int)
    network_permission = RadioField('Network', coerce=int)
    volume_permission = RadioField('Volume', coerce=int)
    endpoint_permission = RadioField('Endpoint', coerce=int)
