from flask import Blueprint

bp = Blueprint('volume', __name__)

from app.volume import routes
