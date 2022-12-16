import requests
import base64
import json
import hashlib
from loguru import logger


GIHS_url_stensil    = "https://api.github.com/repos/{owner}/{repo}/contents/{path}/{filename}"
GIHS_cdn_stensil    = "https://cdn.jsdelivr.net/gh/{owner}/{repo}/{path}/{filename}"

class GITHUB:
    # 把GitHub图床翻译成 GitHub Image Hosting Service, 然后取他的简写为GIHS。
    GIHS_REPO           = "images-1"
    GIHS_PATH           = "test"
    # GitHub issues 仓库
    # TOKEN = "ghu_XuUkXX4btBCFi48Nt4I3GuwaSnvqV70uYr2o"
    TOKEN = "ghu_vgrYndRjJ5CeaoJRmsIucpE32RggHV0GmxyQ"
    OWNER = 'shaoyaoqian'
    REPO  = "MerryJingle"

# GitHub App
APP_ID        = "272667"
client_id     = "Iv1.d5df482df1cd3635"
client_secret = "c9a7b1d853d87a138923951ba47e3c8fadd2d26b"

APP_RSA_FILE = "wechat-to-issues.2022-12-14.private-key.pem"

def GIHS_upload_file(githubuser,filename):
    logger.info("GIHS_upload_file")
    def open_file(file_path):
        with open(file_path, 'rb') as f:
            return f.read()
    def file_base64(data):
        sha = CalcSha1(data)
        print(sha)
        data_b64 = base64.b64encode(data).decode('utf-8')
        return data_b64, sha
    def CalcSha1(data):
        sha1obj = hashlib.sha1()
        head = 'blob {}\0'.format(len(data))
        sha1obj.update(head.encode('utf-8'))
        sha1obj.update(data)
        hash = sha1obj.hexdigest()
        return hash
    file_data = open_file(filename)
    url = GIHS_url_stensil.format(owner=githubuser.OWNER, repo=githubuser.GIHS_REPO, path=githubuser.GIHS_PATH, filename=filename)
    headers = {"Authorization": "token " + githubuser.TOKEN}
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
    response = requests.put(url=url, data=json.dumps(data), headers=headers)
    logger.info(response.json())
    response.encoding = "utf-8"
    re_data = json.loads(response.text)
    # 能返回文件sha值表示上传成功
    print(re_data)
    print(re_data['content']['sha']) 
    # 在国内默认的down_url可能会无法访问，因此使用CDN访问
    return GIHS_cdn_stensil .format(owner=githubuser.OWNER, repo=githubuser.GIHS_REPO, path=githubuser.GIHS_PATH, filename=filename)


def create_github_issue(githubuser,title,body):
    logger.info("create_github_issue")
    url_base = "https://api.github.com/repos/{OWNER}/{REPO}/issues"
    url = url_base.format(OWNER=githubuser.OWNER, REPO=githubuser.REPO)
    headers = {"Authorization": "Bearer " + githubuser.TOKEN}
    data = {
        "title": title,
        "body": body,
    }
    response = requests.post(url=url, data=json.dumps(data), headers=headers)
    logger.info(response.json())
    message = "成功发布动态！\n仓库：{}\n日期：{}\n内容：{}\n".format(
        '{}/{}'.format(githubuser.OWNER, githubuser.REPO),
        response.json()['title'],
        response.json()['body'])
    logger.info(message)
    return message


def user_access_token(code):
    logger.info("user_access_token")
    url = "https://github.com/login/oauth/access_token"
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code
    }
    headers = { 'accept': 'application/json' }
    response = requests.post(url,params=params, headers=headers, timeout=1)
    logger.info(response.json())
    return response.json()['access_token']


def user_id(githubuser):
    logger.info("user_id")
    url_user = "https://api.github.com/user"
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer " + githubuser.TOKEN,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    response = requests.get(url_user,headers=headers)
    logger.info(response.url)
    logger.info(response.json())
    return response.json()['id']


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
