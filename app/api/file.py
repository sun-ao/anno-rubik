from flask import Blueprint, current_app, request, jsonify
from qcloud_cos import CosConfig, CosS3Client
from datetime import datetime

file_bp = Blueprint('file', __name__)

@file_bp.route('/upload_file', methods=['POST'])
def upload_file():
    # 实现文件上传逻辑
    try:
        file = request.files.get('file')

        # 获取 COS 配置信息
        cos_region = current_app.config['COS_REGION']
        cos_secret_id = current_app.config['COS_SECRET_ID']
        cos_secret_key = current_app.config['COS_SECRET_KEY']
        cos_bucket_name = current_app.config['COS_BUCKET_NAME']

        # 初始化 COS 配置
        cos_config = CosConfig(Region=cos_region, SecretId=cos_secret_id, SecretKey=cos_secret_key)
        cos_client = CosS3Client(cos_config)

        if file:
            # 将文件上传至腾讯云 COS
            response = cos_client.put_object(
                Bucket=cos_bucket_name,
                Body=file.read(),
                Key=("/" + datetime.now().strftime("%Y%m%d%H%M%S") + "/" + file.filename)
            )
            # 返回上传结果
            return jsonify({'message': 'File uploaded successfully.', 'data': str(response)}) 
        else:
            return jsonify({'message': 'No file found in the request.'}), 500
    except Exception as e:
        error_message = str(e)
        return jsonify({'message': 'Failed to upload file.', 'error': error_message}), 500
        