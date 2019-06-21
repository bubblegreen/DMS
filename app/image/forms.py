from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.validators import ValidationError, DataRequired
from app.models import Group
from flask import current_app
import tempfile


class ImagePullForm(FlaskForm):
    name = StringField('Image', validators=[DataRequired()])
    registry = SelectField('Registry', default=1, coerce=int)

    def validate_name(self, name):
        repo_name = name.data.split('/')
        tag_name = name.data.split(':')
        if len(tag_name) > 2 \
                or len(repo_name) > 2 \
                or repo_name[0] == '' \
                or tag_name[-1] == '' \
                or '/' in tag_name[-1]:
            raise ValidationError('镜像名输入有误，请重新输入！')


class ImageBuildForm(FlaskForm):
    name = StringField('Image', validators=[DataRequired()])
    # TODO
