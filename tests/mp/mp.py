import os
import requests
import json
from PIL import Image
from io import BytesIO
import time

# 裁剪图片（适合微信公众号封面：2.35:1）
def crop_to_aspect(image, aspect_ratio):
    img_width, img_height = image.size
    target_width = img_width
    target_height = int(img_width / aspect_ratio)

    if target_height > img_height:
        target_height = img_height
        target_width = int(img_height * aspect_ratio)

    left = (img_width - target_width) / 2
    top = (img_height - target_height) / 2
    right = (img_width + target_width) / 2
    bottom = (img_height + target_height) / 2

    return image.crop((left, top, right, bottom))

# 获取微信鉴权
def get_wechat_access_token(appid, secret):
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}"
    response = requests.get(url)
    return response.json()['access_token']

# 上传图片素材（永久素材）
def upload_image_to_wechat(image_path, type, access_token):
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type={type}"
    with open(image_path, 'rb') as img:
        files = {'media': img}
        response = requests.post(url, files=files)
    return response.json()

# 新建草稿
def add_draft_to_wechat(data, access_token):
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    response = requests.post(url, headers=headers, data=json.dumps(data, ensure_ascii=False).encode('utf-8'))
    return response.json()

# 发布
def submit_to_wechat(media_id, access_token):
    url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={access_token}"
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    data = {
        "media_id": media_id
    }
    response = requests.post(url, headers=headers, data=json.dumps(data, ensure_ascii=False).encode('utf-8'))
    return response.json()

# 是否包含中文
def contains_chinese(s):
    for c in s:
        if '\u4e00' <= c <= '\u9fff':
            return True
    return False

# TODO 请填写你的 appid 和 secret 
access_token = get_wechat_access_token("appid", "secret")

try:
    title_response = requests.get('https://api.oioweb.cn/api/common/yiyan', timeout=10)
    data_title = title_response.json()['result']['content']
    data_from = title_response.json()['result']['from']
    data_author = title_response.json()['result']['author']
    image_url = title_response.json()['result']['pic_url']
    image_date = title_response.json()['result']['date']
except Exception as e:
    # 在异常发生时返回空对象
    data_title = data_from = data_author = image_url = image_date = None

today_date = time.strftime('%Y%m%d', time.localtime(time.time()))
# 判断时间不为当天
if image_date != today_date:
    image_date = today_date
    random_response = requests.get('https://v1.hitokoto.cn/')
    data_title = random_response.json()['hitokoto']
    data_from = random_response.json()['from']
    data_author = random_response.json()['from_who']
    image_url = "https://picsum.photos/1366/768?random"
image_response = requests.get(image_url)
original_img = Image.open(BytesIO(image_response.content))
cropped_img = crop_to_aspect(original_img, 2.35 / 1)

# 保存原图并转换为JPEG格式并上传
original_temp_name = f"original_{image_date}.jpg"
original_img.save(original_temp_name, 'JPEG')
original_upload_response = upload_image_to_wechat(original_temp_name, 'image', access_token)
data_image = original_upload_response['url']
os.remove(original_temp_name)

# 裁剪图片并保存为JPEG格式并上传
cropped_temp_name = f"cropped_{image_date}.jpg"
cropped_img.save(cropped_temp_name, 'JPEG')
cropped_upload_response = upload_image_to_wechat(cropped_temp_name, 'image', access_token)
data_thumb_media_id = cropped_upload_response['media_id']
os.remove(cropped_temp_name)

try:
    english_response = requests.get('https://api.oioweb.cn/api/common/OneDayEnglish', timeout=10)
    data_english = english_response.json()['result']['content']
    data_english_note = english_response.json()['result']['note']
except Exception as e:
    # 在异常发生时返回空对象
    # 获取英文名言
    quote_url = 'https://api.quotable.io/random'
    quote_response = requests.get(quote_url)
    quote_data = quote_response.json()
    data_english = quote_data['content']

    # 使用 LibreTranslate API 将英文名言翻译成中文
    translate_url = 'https://api.mymemory.translated.net/get'
    translate_params = {
        'q': data_english,
        'langpair': 'en|zh'
    }
    translate_response = requests.get(translate_url, params=translate_params)
    translate_data = translate_response.json()
    data_english_note = translate_data['responseData']['translatedText']

chinese_response = requests.get('https://v1.hitokoto.cn/')
data_chinese = chinese_response.json()['hitokoto']
while True:
    if contains_chinese(data_chinese):
        break
    chinese_response = requests.get('https://v1.hitokoto.cn/')
    data_chinese = chinese_response.json()['hitokoto']
    
data_content = f'''<p><span style="font-size: 14px;">标题来源：{data_from}（{data_author}）</span></p><p><span style="font-size: 14px;"><br  /></span></p><p><img class="rich_pages wxw-img" data-ratio="0.562037037037037" data-src="{data_image}" data-w="1080"></p><p><br  /></p><h2 style="text-align: center;"><span style="font-size: 18px;"><strong>每日一句英文</strong></span></h2><p><br  /></p><p>{data_english}</p><p>{data_english_note}</p><p><br  /></p><h2 style="text-align: center;"><span style="font-size: 18px;"><strong>每日一句中文</strong></span></h2><p><br  /></p><p>{data_chinese}</p><p><br  /></p><hr style="border-style: solid;border-width: 1px 0 0;border-color: rgba(0,0,0,0.1);-webkit-transform-origin: 0 0;-webkit-transform: scale(1, 0.5);transform-origin: 0 0;transform: scale(1, 0.5);"  /><p style="text-align: right;"><span style="font-size: 12px;">如有侵权，请联系我，我将及时删除或更正。</span></p>'''

data = {
    "articles": [
        {
            "title": data_title,
            "author": "x.notes",
            "digest": "",
            "content": data_content,
            "content_source_url": "",
            "thumb_media_id": data_thumb_media_id,
            "need_open_comment": 1,
            "only_fans_can_comment": 0
        }
    ]
}
add_draft_response = add_draft_to_wechat(data, access_token)
# draft_media_id = add_draft_response['media_id']

# submit_to_wechat(draft_media_id, access_token)
