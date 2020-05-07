from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, RadioField, BooleanField, widgets
from wtforms.validators import DataRequired, ValidationError
from app.utils.field import LabelsField, VolumesField


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class DockerServerForm(FlaskForm):
    servers = MultiCheckboxField()
