from flask import Blueprint

api_bp = Blueprint('api', __name__)

from app.api.file import file_bp
from app.api.cube import cube_bp
from app.api.proxy import proxy_bp

api_bp.register_blueprint(file_bp)
api_bp.register_blueprint(cube_bp)
api_bp.register_blueprint(proxy_bp)


