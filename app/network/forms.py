from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, BooleanField
from wtforms.validators import ValidationError, DataRequired
from app.utils.field import LabelsField
from app.models import Endpoint
from app.utils.docker import docker_client
from docker.errors import NotFound


class NetworkCreateForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired()])
    driver = SelectField('Driver',
                         choices=[('bridge', 'bridge'), ('host', 'host'), ('null', 'null'), ('overlay', 'overlay')])
    options = LabelsField(key_name='opt_name', value_name='opt_value')
    opt_name = StringField('name')
    opt_value = StringField('value')
    subnet = StringField('Subnet')
    gateway = StringField('Gateway')
    ip_range = StringField('IP range')
    exclude_ips = StringField('Exclude IPs')
    labels = LabelsField()
    label_name = StringField('name')
    label_value = StringField('value')
    internal = BooleanField('Restrict external access to the network: ')
    attachable = BooleanField('Enable manual container attachment: ')
    access = SelectField('权限范围', choices=[(1, '不可见'), (2, '组内'), (3, '公开')], coerce=int)
    groups = SelectMultipleField('组', coerce=int)

    def validate_name(self, name):
        endpoint = Endpoint.query.get(session.get('endpoint_id'))
        try:
            network = docker_client(endpoint.url).networks.get(name.data)
        except NotFound:
            network = None
        if network:
            raise ValidationError('Network名称已存在，请重新输入!')
