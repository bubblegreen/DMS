from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, RadioField, BooleanField
from wtforms.validators import DataRequired, ValidationError
from app.utils.field import LabelsField, VolumesField


class ContainerCreateForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    image = SelectField('Image')
    publish_all_port = BooleanField('Publish all export ports')
    publish_port = LabelsField('Publish port', key_name='host_port', value_name='container_port')
    host_port = StringField()
    container_port = StringField()
    access = SelectField('权限范围', choices=[(1, '不可见'), (2, '组内'), (3, '公开')], coerce=int)
    groups = SelectMultipleField('组', coerce=int)
    auto_remove = BooleanField('Auto Remove')
    command = StringField('Command')
    entrypoint = StringField('Entry Point')
    workdir = StringField('Working Dir')
    user = StringField('User')
    volume = VolumesField()
    volume_name = SelectField()
    bind_path = StringField()
    network = SelectField('Network')
    hostname = StringField('Hostname')
    domain = StringField('Domain Name')
    mac = StringField('Mac Address')
    ip4 = StringField('IP4 Address')
    ip6 = StringField('IP6 Address')
    env = LabelsField('ENV', key_name='env_name', value_name='env_value')
    env_name = StringField()
    env_value = StringField()
    labels = LabelsField('Labels')
    label_name = StringField()
    label_value = StringField()
    restart = SelectField('Restart Policy',
                         choices=(('never', 'Never'), ('always', 'Always'), ('on-failure', 'On failure')))
    privileged = BooleanField('Privileged mode')
    devices = LabelsField('device', key_name='dev_host', value_name='dev_container')
    dev_host = StringField()
    dev_container = StringField()
    mem_soft_limit = StringField('Memory reservation')
    mem_limit = StringField('Memory limit')
    cpu = StringField('CPU limit')
