from flask import Blueprint

bp = Blueprint('toolbox', __name__)

from app.toolbox import routes
