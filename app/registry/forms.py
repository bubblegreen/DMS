from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField, SelectField
from wtforms.validators import ValidationError, DataRequired
from app.models import Registry
from app.utils.docker import docker_client
from docker.errors import DockerException
from flask import current_app
import requests
from sqlalchemy import or_


class AddRegistryForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired()])
    access = SelectField('权限范围', choices=[(1, '不可见'), (2, '组内'), (3, '公开')], coerce=int)
    groups = SelectMultipleField('组', coerce=int)

    def validate_name(self, name):
        registry = Registry.query.filter(Registry.name == name.data).first()
        if registry is not None:
            current_app.logger.error('Name Error')
            raise ValidationError('名称已存在，请重新输入！')

    def validate_url(self, url):
        registry = Registry.query.filter(or_(Registry.url == url.data, Registry.url == url.data.strip('/'))).first()
        if registry is not None:
            current_app.logger.error('URL Error')
            raise ValidationError('URL已存在，请重新输入！')
        try:
            res = requests.get(url.strip('/') + '/v2/')
            if res.status_code != 200:
                raise ValueError('URL输入有误，请检查！')
            # docker_client(url.data)
        except Exception as ex:
            current_app.logger.error('Connect Error')
            raise ValidationError('URL输入有误，请检查！')


class UpdateRegistryForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired()])
    access = SelectField('权限范围', choices=[(1, '不可见'), (2, '组内'), (3, '公开')], coerce=int)
    groups = SelectMultipleField('组', coerce=int)

    def validate_url(self, url):
        try:
            res = requests.get(url.strip('/') + '/v2/')
            if res.status_code != 200:
                raise ValueError('URL已存在，请重新输入！')
            docker_client(url.data)
        except DockerException as ex:
            current_app.logger.error('Docker Error')
            raise ValidationError('URL输入有误，请检查！')
