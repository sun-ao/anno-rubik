from flask import Blueprint, current_app, request, jsonify
import mysql.connector
import json

log_bp = Blueprint('log', __name__)

# 初始化 MySQL 连接
def init_mysql_connection():
    MYSQL_HOST = current_app.config['MYSQL_HOST']
    MYSQL_PORT = current_app.config['MYSQL_PORT']
    MYSQL_USER = current_app.config['MYSQL_USER']
    MYSQL_PASSWORD = current_app.config['MYSQL_PASSWORD']
    MYSQL_DB = current_app.config['MYSQL_DB']
    
    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )

# 初始化 MySQL 游标
def init_mysql_cursor(mysql_connection):
    return mysql_connection.cursor()

# 创建数据库表
def create_track_log_table():
    mysql_connection = init_mysql_connection()
    mysql_cursor = init_mysql_cursor(mysql_connection)
    
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS track_log (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ip VARCHAR(64) NULL,
        content JSON NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    '''
    mysql_cursor.execute(create_table_query)
    mysql_connection.commit()

# 存储缓存的方法
def save_log(ip, content):
    mysql_connection = init_mysql_connection()
    mysql_cursor = init_mysql_cursor(mysql_connection)
    
    mysql_cursor.execute('''
        INSERT INTO track_log (ip, content)
        VALUES (%s, %s)
    ''', (ip, json.dumps(content)))
    mysql_connection.commit()

def get_real_ip(request):
    # 尝试从X-Forwarded-For头部获取IP地址
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        # X-Forwarded-For可能包含多个IP地址，第一个通常是真实的客户端IP
        ip = x_forwarded_for.split(',')[0]
    else:
        # 如果没有X-Forwarded-For头部，尝试从X-Real-IP获取
        ip = request.headers.get('X-Real-IP')
    if not ip:
        # 如果上述头部都不存在，回退到remote_addr
        ip = request.remote_addr
    return ip

@log_bp.route('/log', methods=['GET', 'POST'])
def log_request():
    try:
        # 收集请求IP
        request_ip = get_real_ip(request)
        # 初始化一个空字典来存储参数
        request_params = {}
        
        # 提取查询参数
        query_params = request.args.to_dict()
        request_params.update(query_params)
        
        # 对于POST和其他非GET请求，提取请求体中的参数
        if request.method != 'GET':
            if request.is_json:
                # 处理JSON类型的请求体
                body_params = request.get_json()
                request_params.update(body_params)
            else:
                # 处理表单数据类型的请求体
                body_params = request.form.to_dict()
                request_params.update(body_params)

        # return jsonify(request_params)
        save_log(request_ip, request_params)

        return jsonify({'message': 'log successfully.'})
    except Exception as e:
        error_message = str(e)
        return jsonify({'error': 'Failed to track log.', 'message': error_message}), 500
