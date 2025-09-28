from flask import Blueprint

operaciones_bp = Blueprint('operaciones', __name__, template_folder='templates')

from . import routes
