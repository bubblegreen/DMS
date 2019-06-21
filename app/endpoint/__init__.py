from flask import Blueprint

bp = Blueprint('endpoint', __name__)

from app.endpoint import routes
