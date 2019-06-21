from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField, SelectField
from wtforms.validators import ValidationError, DataRequired
from app.models import Endpoint
from app.utils.docker import docker_client
from docker.errors import DockerException
from flask import current_app


class AddEndpointForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired()])
    access = SelectField('权限范围', choices=[(1, '不可见'), (2, '组内'), (3, '公开')], coerce=int)
    groups = SelectMultipleField('组', coerce=int)

    def validate_name(self, name):
        endpoint = Endpoint.query.filter(Endpoint.name == name.data).first()
        if endpoint is not None:
            current_app.logger.error('Name Error')
            raise ValidationError('名称已存在，请重新输入！')

    def validate_url(self, url):
        endpoint = Endpoint.query.filter(Endpoint.url == url.data).first()
        if endpoint is not None:
            current_app.logger.error('URL Error')
            raise ValidationError('URL已存在，请重新输入！')
        try:
            docker_client(url.data)
        except DockerException as ex:
            current_app.logger.error('Docker Error')
            raise ValidationError('URL输入有误，请检查！')


class UpdateEndpointForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired()])
    access = SelectField('权限范围', choices=[(1, '不可见'), (2, '组内'), (3, '公开')], coerce=int)
    groups = SelectMultipleField('组', coerce=int)

    def validate_url(self, url):
        try:
            docker_client(url.data)
        except DockerException as ex:
            current_app.logger.error('Docker Error')
            raise ValidationError('URL输入有误，请检查！')
