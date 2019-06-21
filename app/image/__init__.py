from flask import Blueprint

bp = Blueprint('image', __name__)

from app.image import routes