from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField
from wtforms.validators import ValidationError, DataRequired
from app.models import Endpoint
from flask import session
from app.utils.docker import docker_client
from docker.errors import NotFound
from app.utils.field import LabelsField


class VolumeCreateForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired()])
    driver = SelectField('Driver', choices=[('local', 'local'), ])
    label_name = StringField('name')
    label_value = StringField('value')
    labels = LabelsField()
    access = SelectField('权限范围', choices=[(1, '不可见'), (2, '组内'), (3, '公开')], coerce=int)
    groups = SelectMultipleField('组', coerce=int)

    def validate_name(self, name):
        endpoint = Endpoint.query.get(session.get('endpoint_id'))
        try:
            volume = docker_client(endpoint.url).volumes.get(name.data)
        except NotFound:
            volume = None
        if volume:
            raise ValidationError('Volume名称已存在，请重新输入!')
