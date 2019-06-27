from flask import Blueprint

bp = Blueprint('network', __name__)

from app.network import routes
