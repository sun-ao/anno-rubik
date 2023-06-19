from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
app.config.from_pyfile('config.py')

# 初始化 CORS 扩展
CORS(app)

from app.api import api_bp
app.register_blueprint(api_bp)
