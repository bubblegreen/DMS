from flask import Blueprint

bp = Blueprint('container', __name__)

from app.container import routes
