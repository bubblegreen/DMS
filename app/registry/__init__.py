from flask import Blueprint

bp = Blueprint('registry', __name__)

from app.registry import routes
