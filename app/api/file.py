from flask import Blueprint, current_app, request, jsonify
from qcloud_cos import CosConfig, CosS3Client
from datetime import datetime
from sts.sts import Sts

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
                Key=(datetime.now().strftime("%Y%m%d%H%M%S") + "/" + file.filename)
            )
            # 返回上传结果
            return jsonify({'message': 'File uploaded successfully.', 'data': str(response)}) 
        else:
            return jsonify({'message': 'No file found in the request.'}), 500
    except Exception as e:
        error_message = str(e)
        return jsonify({'message': 'Failed to upload file.', 'error': error_message}), 500
    
@file_bp.route('/get_upload_sts', methods=['POST'])
def get_upload_sts():
    # 实现文件上传逻辑
    try:
        allow_path_prefix = datetime.now().strftime("%Y%m%d") + "/" + datetime.now().strftime("%H%M%S")  + "/" 
        config = {
            # 请求URL，域名部分必须和domain保持一致
            # 使用外网域名时：https://sts.tencentcloudapi.com/
            # 使用内网域名时：https://sts.internal.tencentcloudapi.com/
            'url': 'https://sts.tencentcloudapi.com/',
            # 域名，非必须，默认为 sts.tencentcloudapi.com
            # 内网域名：sts.internal.tencentcloudapi.com
            'domain': 'sts.tencentcloudapi.com', 
            # 临时密钥有效时长，单位是秒
            'duration_seconds': 1800,
            'secret_id': current_app.config['COS_SECRET_ID'],
            # 固定密钥
            'secret_key': current_app.config['COS_SECRET_KEY'],
            # 换成你的 bucket
            'bucket': current_app.config['COS_BUCKET_NAME'],
            # 换成 bucket 所在地区
            'region': current_app.config['COS_REGION'],
            # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
            # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
            'allow_prefix': [allow_path_prefix + "*"],
            # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
            'allow_actions': [
                # 简单上传
                'name/cos:PutObject',
                'name/cos:PostObject',
                # 分片上传
                'name/cos:InitiateMultipartUpload',
                'name/cos:ListMultipartUploads',
                'name/cos:ListParts',
                'name/cos:UploadPart',
                'name/cos:CompleteMultipartUpload'
            ]
        }
        sts = Sts(config)
        response = sts.get_credential()
        return jsonify({
            'bucket': config['bucket'],
            'region': config['region'],
            'allow_path_prefix': allow_path_prefix,
            'sts': response
        })
    except Exception as e:
        error_message = str(e)
        return jsonify({'message': 'Failed to get STS.', 'error': error_message}), 500
        