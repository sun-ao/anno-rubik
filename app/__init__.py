from flask import Flask
from flask_cors import CORS
from app.api import api_bp
from app.api.proxy import create_proxy_cache_table  # 导入初始化函数
from app.api.log import create_track_log_table  # 导入初始化函数

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    # 初始化 CORS 扩展
    CORS(app)

    # 在应用工厂函数中执行应用级别初始化
    with app.app_context():
        create_proxy_cache_table()
        create_track_log_table()

    # 注册蓝图
    app.register_blueprint(api_bp)

    return app
