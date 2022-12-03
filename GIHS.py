import requests
import base64
import json
import hashlib

# 参数设置
# 我把GitHub图床翻译成 GitHub Image Hosting Service, 然后取他的简写为GIHS。
GIHS_OWNER   = "shaoyaoqian"
GIHS_REPO    = "images-1"
GIHS_PATH    = "test"
GITHUB_TOKEN = "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"
url_stensil  = "https://api.github.com/repos/{owner}/{repo}/contents/{path}/{filename}"
cdn_stensil  = "https://cdn.jsdelivr.net/gh/{owner}/{repo}/{path}/{filename}"

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

def upload_file(filename):
    file_data = open_file(filename)
    token = GITHUB_TOKEN
    url = url_stensil.format(owner=GIHS_OWNER, repo=GIHS_REPO, path=GIHS_PATH, filename=filename)
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
    req = requests.put(url=url, data=data, headers=headers)
    req.encoding = "utf-8"
    re_data = json.loads(req.text)
    # 能返回文件sha值表示上传成功
    print(re_data)
    print(re_data['content']['sha']) 
    # 在国内默认的down_url可能会无法访问，因此使用CDN访问
    return cdn_stensil.format(owner=GIHS_OWNER, repo=GIHS_REPO, path=GIHS_PATH, filename=filename)

if __name__ == '__main__':
    filename = "a.jpeg"
    upload_file(filename)