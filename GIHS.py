import requests
import base64
import json
import hashlib
from loguru import logger

# 把GitHub图床翻译成 GitHub Image Hosting Service, 然后取他的简写为GIHS。
GIHS_OWNER          = "shaoyaoqian"
GIHS_REPO           = "alice-player"
GIHS_PATH           = "test"
GIHS_url_stensil    = "https://api.github.com/repos/{owner}/{repo}/contents/{path}/{filename}"
GIHS_cdn_stensil    = "https://cdn.jsdelivr.net/gh/{owner}/{repo}/{path}/{filename}"

# GitHub issues 仓库
GITHUB_TOKEN = "ghu_RjTyVDgluFzDUEP8NSA7rQnlQRns7k4fXpjV"
GITHUB_OWNER = 'shaoyaoqian'
GITHUB_REPO  = "alice-player"

# GitHub App
APP_ID        = "272667"
client_id     = "Iv1.d5df482df1cd3635"
client_secret = "c9a7b1d853d87a138923951ba47e3c8fadd2d26b"

APP_RSA_FILE = "wechat-to-issues.2022-12-14.private-key.pem"

def GIHS_upload_file(filename):
    logger.info("GIHS_upload_file")
    # 读取文件
    def open_file(file_path):
        with open(file_path, 'rb') as f:
            return f.read()
    # 将文件转换为base64编码，上传文件必须将文件以base64格式上传
    def file_base64(data):
        sha = CalcSha1(data)
        print(sha)
        data_b64 = base64.b64encode(data).decode('utf-8')
        return data_b64, sha
    def CalcSha1(data):
        # 哈希值的计算：https://stackoverflow.com/questions/7225313/how-does-git-compute-file-hashes/7225329#7225329
        # 需要在原数据前加上 "blob {字节长度}\0"
        sha1obj = hashlib.sha1()
        head = 'blob {}\0'.format(len(data))
        sha1obj.update(head.encode('utf-8'))
        sha1obj.update(data)
        hash = sha1obj.hexdigest()
        return hash
    file_data = open_file(filename)
    token = GITHUB_TOKEN
    url = GIHS_url_stensil.format(owner=GIHS_OWNER, repo=GIHS_REPO, path=GIHS_PATH, filename=filename)
    headers = {"Authorization": "token " + token}
    content, sha = file_base64(file_data)
    data = {
        "message": "Add a new file.",
        "committer": {
            "name": "robot",
            "email": "github@robot.com"
        },
        "sha":sha,
        "content": content
    }
    data = json.dumps(data)
    response = requests.put(url=url, data=data, headers=headers)
    response.encoding = "utf-8"
    re_data = json.loads(response.text)
    # 能返回文件sha值表示上传成功
    print(re_data)
    print(re_data['content']['sha']) 
    # 在国内默认的down_url可能会无法访问，因此使用CDN访问
    return GIHS_cdn_stensil .format(owner=GIHS_OWNER, repo=GIHS_REPO, path=GIHS_PATH, filename=filename)

def create_github_issue(title,body):
    logger.info("create_github_issue")
    token = GITHUB_TOKEN
    url_base = "https://api.github.com/repos/{OWNER}/{REPO}/issues"
    url = url_base.format(OWNER=GIHS_OWNER, REPO=GIHS_REPO)
    # headers = {"Authorization": "token " + token}
    headers = {"Authorization": "token " + token}
    # "Accept: application/vnd.github+json" \
    # "Authorization: Bearer <YOUR-TOKEN>"\
    # "X-GitHub-Api-Version: 2022-11-28" \
    data = {
        "title": title,
        "body": body,
    }
    data = json.dumps(data)
    response = requests.post(url=url, data=data, headers=headers)
    message = "成功发布动态！\n日期：{}\n内容：{}\n".format(response.json()['title'],response.json()['body'])
    logger.info(message)
    return message


def user_access_token(code):
    logger.info("user_access_token")
    url_access_token = "https://github.com/login/oauth/access_token"
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code
    }
    headers = {
        'accept': 'application/json'
    }
    response = requests.post(url_access_token,params=params, headers=headers, timeout=1)
    # {'access_token': 'ghu_1X6zMvZQQxXSDKWxamtQQQFrtBzoRG3Dtaez', 'expires_in': 28800, 
    # 'refresh_token': 'ghr_1PfEuwbCDqJ5uqzyIGQsj0Nma4erXj1UCM9kMPD94q4VTr1VIdSnWVAxpzUUGWuXXjzYzl4ZB5GU', 
    # 'refresh_token_expires_in': 15724800, 'token_type': 'bearer', 'scope': ''}
    return response.json()['access_token']


def installation_access_token(installation_id):
    # 生成JWT令牌
    logger.info("installation_access_token")
    key = open(APP_RSA_FILE, 'r').read()
    url_app          = "https://api.github.com/app"
    url_access_token = 'https://api.github.com/app/installations/{installation_id}/access_tokens'
    authorization    = '"Authorization: Bearer {YOUR_JWT}"'
    payload = {
        'iat': int(time.time())-100,
        'exp': int(time.time())+500,
        'iss': APP_ID
    }
    JWT_token = jwt.encode(payload=payload, key=key, algorithm='RS256')
    headers   = {
        "Authorization": "Bearer " + JWT_token,
        "Accept": "application/vnd.github+json"
    }
    response = requests.post(url_access_token.format(installation_id=installation_id), headers=headers)
    print(response.json())
    return response

if __name__ == '__main__':
    filename = "a.jpeg"
    upload_file(filename)