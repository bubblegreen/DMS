from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField
from wtforms.validators import ValidationError, DataRequired
from app.models import Group
from flask import current_app


class AddGroupForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired()])
    desc = StringField('说明')
    members = SelectMultipleField('成员', coerce=int)

    def validate_name(self, name):
        group = Group.query.filter(Group.name == name.data).first()
        if group is not None:
            current_app.logger.error('Name Error')
            raise ValidationError('名称已存在，请重新输入！')


class UpdateGroupForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired()])
    desc = StringField('说明')
    members = SelectMultipleField('成员', coerce=int)
