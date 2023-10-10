from flask import Blueprint, current_app, request, jsonify
import mysql.connector
import hashlib
import json
import requests
from urllib.parse import unquote
from cryptography.fernet import Fernet

proxy_bp = Blueprint('proxy', __name__)

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

# 辅助函数：生成请求参数的哈希值
def generate_request_hash(params):
    sorted_params = sorted(params.items())
    hash_input = ''.join([str(param) for param in sorted_params])
    return hashlib.sha256(hash_input.encode()).hexdigest()

# 创建数据库表
def create_proxy_cache_table():
    mysql_connection = init_mysql_connection()
    mysql_cursor = init_mysql_cursor(mysql_connection)
    
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS proxy_cache (
        id INT AUTO_INCREMENT PRIMARY KEY,
        request_hash VARCHAR(64) NOT NULL,
        request_data JSON NOT NULL,
        response_data JSON NOT NULL,
        status_code INT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    '''
    mysql_cursor.execute(create_table_query)
    mysql_connection.commit()

# 查询缓存的方法
def get_cached_response(request_hash):
    mysql_connection = init_mysql_connection()
    mysql_cursor = init_mysql_cursor(mysql_connection)
    
    mysql_cursor.execute('''
        SELECT response_data, status_code
        FROM proxy_cache
        WHERE request_hash = %s
        ORDER BY created_at DESC
        LIMIT 1
    ''', (request_hash,))
    cache_data = mysql_cursor.fetchone()
    
    if cache_data:
        response_data, status_code = cache_data
        return json.loads(response_data), status_code
    else:
        return None

# 存储缓存的方法
def cache_response(request_hash, request_data, response_data, status_code):
    mysql_connection = init_mysql_connection()
    mysql_cursor = init_mysql_cursor(mysql_connection)
    
    mysql_cursor.execute('''
        INSERT INTO proxy_cache (request_hash, request_data, response_data, status_code)
        VALUES (%s, %s, %s, %s)
    ''', (request_hash, json.dumps(request_data), json.dumps(response_data), status_code))
    mysql_connection.commit()

# 生成加密密钥（仅在首次使用时执行，然后将密钥保存在安全的地方）
def generate_fernet_key():
    key = Fernet.generate_key()
    print(key.decode())
    return key

@proxy_bp.route('/generate_fernet_key', methods=['GET'])
def generate_fernet_key_request():
    key = generate_fernet_key()
    return key, 200
        
# 初始化 Fernet 加密器
def init_fernet_encryptor():
    key = current_app.config['FERNET_KEY']  # 从应用配置中获取密钥
    return Fernet(key)

# 加密 URL
def encrypt_url(url):
    fernet = init_fernet_encryptor()
    encrypted_url = fernet.encrypt(url.encode('utf-8')).decode('utf-8')
    return encrypted_url

@proxy_bp.route('/encrypt', methods=['GET'])
def encrypt_request():
    text = unquote(request.args.get('text'))
    return encrypt_url(text), 200

# 解密 URL
def decrypt_url(encrypted_url):
    fernet = init_fernet_encryptor()
    decrypted_url = fernet.decrypt(encrypted_url.encode('utf-8')).decode('utf-8')
    return decrypted_url

@proxy_bp.route('/proxy', methods=['GET', 'POST'])
def proxy_request():
    try:
        request_method = request.method
        request_headers = dict(request.headers)
        request_url = unquote(request.args.get('_url'))
        # 支持加密传输
        if not request_url.startswith('http'):
             request_url = decrypt_url(request_url)
        request_params = None

        if request_method == 'POST':
            # 检查请求的 Content-Type 头是否为 application/json
            content_type = request_headers.get('Content-Type', '')
            if content_type.startswith('application/json'):
                request_params = request.json  # 获取 JSON 请求体数据
            else:
                return jsonify({'error': 'Unsupported Content-Type'}), 400

        request_data = {
            'url': request_url,
            'method': request_method,
            'data': request_params
        }
        request_hash = generate_request_hash(request_data)
        forcenocache = request.args.get('_nocache') == '1'  # 请求参数：是否强制不使用缓存

        if not forcenocache:
            cached_response = get_cached_response(request_hash)
            if cached_response:
                response, status_code = cached_response
                return jsonify(response), status_code

        target_response = requests.request(
            method=request_method,
            url=request_url,
            json=request_params
        )
        status_code = target_response.status_code
        response_headers = dict(target_response.headers)
        response_text = target_response.text
        response_data = {
            "headers": response_headers,
            "data": response_text
        }

        cache_response(request_hash, request_data, response_data, status_code)

        return jsonify(response_data), status_code
    except Exception as e:
        error_message = str(e)
        return jsonify({'error': 'Failed to proxy request.', 'message': error_message}), 500
