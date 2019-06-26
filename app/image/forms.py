from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, RadioField, TextAreaField, FileField
from wtforms.validators import ValidationError, DataRequired, regexp, optional
import re
from app.utils.docker import docker_client
from flask import session
from app.models import Endpoint


class ImagePullForm(FlaskForm):
    name = StringField('Image', validators=[DataRequired()])
    registry = SelectField('Registry', default=1, coerce=int)

    def validate_name(self, name):
        if not re.match('(\w+/\w+:\w+)|(\w+:[\w.]+)$', name.data):
            raise ValidationError('镜像名格式输入有误!')
        # repo_name = name.data.split('/')
        # tag_name = name.data.split(':')
        # if len(tag_name) > 2 \
        #         or len(repo_name) > 2 \
        #         or repo_name[0] == '' \
        #         or tag_name[-1] == '' \
        #         or '/' in tag_name[-1]:
        #     raise ValidationError('镜像名输入有误，请重新输入！')


class ImageBuildForm(FlaskForm):
    name = StringField('Image', validators=[DataRequired()])
    access = SelectField('权限范围', choices=[(1, '不可见'), (2, '组内'), (3, '公开')], coerce=int)
    groups = SelectMultipleField('组', coerce=int)
    method = RadioField('Build方法', choices=[('editor', '在线编辑'), ('upload', '上传文件'), ('url', 'Git URL')], default='editor')
    base_image = SelectField('FROM')
    code = TextAreaField('Dockerfile')
    file = FileField('上传文件')
    url = StringField('Git')

    def validate_name(self, name):
        if not re.match('(\w+:\d{1,5}/\w+/\w+:\w+)|(\w+/\w+:\w+)|(\w+:[\w.]+)$', name.data):
            raise ValidationError('名称格式输入有误!')
        endpoint = Endpoint.query.get(session.get('endpoint_id'))
        images = docker_client(endpoint.url).images.list()
        for image in images:
            if name.data in image.tags:
                raise ValidationError('镜像名称重复!')

    def validate_code(self, code):
        for line in code.data.split('\n'):
            if line.lower().strip().startswith('from'):
                raise ValidationError('不需要写入FROM, 请在下拉列表中选择基础镜像！')
