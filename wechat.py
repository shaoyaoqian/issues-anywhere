# coding:utf-8
# 使用前提：云主机(其实用免费的vercel也可以)、域名、微信公众号、七牛云账号、GitHub账号
# 参考 : 
# python 微信公众号开发 后台服务器端配置与公众号开发配置
# https://blog.csdn.net/jinxiaonian11/article/details/104708996/

from flask import Flask, request, abort, render_template
import hashlib
import xmltodict
import time, datetime
import json
import requests
import jwt
from loguru import logger 

# GITHUB 模块
from GIHS import create_github_issue, user_access_token, GITHUB, user_id
from GIHS import GIHS_upload_file as upload_file

githubuser = GITHUB()

# 异步任务池
import asyncio, time, threading
def start_loop(thread_loop):
    asyncio.set_event_loop(thread_loop)
    thread_loop.run_forever()

thread_loop = asyncio.new_event_loop()
threading.Thread(target=start_loop,args=(thread_loop,)).start()

# 微信的token令牌，参数的获取可参考：https://qiniu.pengfeima.cn/typora/202212031457547.png
WECHAT_TOKEN = 'look_back_at_me'
WECHAT_APPID = "wxcc6a1b8adade3237",         
WECHAT_SECRET = "29b97cdfd439873420ecf78e8221fdea"
WECHAT_REGISTER = "n92k"

# 创建一个 Flask 应用
app = Flask(__name__)

@app.route("/github-auth/", methods=["GET", "POST"])
def github():
    code = request.args.get("code")
    access_token = user_access_token(code)
    temp_githubuser = GITHUB()
    temp_githubuser.TOKEN    = access_token
    temp_githubuser.identity = user_id(temp_githubuser)
    # TODO insert a github user
    # database.update(temp_githubuser)
    message = """
    欢迎使用issues-anywhere机器人！ <br><br>
    微信公众号途径：<br>
    &ensp;&ensp;请关注公众号：Donald-Trump <br>
    &ensp;&ensp;您在GitHubID为：{identity} <br>
    &ensp;&ensp;请在公众号发送字符串以绑定身份(首尾无空格): <br>
    &ensp;&ensp;n92k{identity}<br>
    若失效，请点击链接重新登陆：https://github.com/login/oauth/authorize?client_id=Iv1.d5df482df1cd3635
    """
    return message.format(identity=temp_githubuser.identity)

@app.route("/", methods=["GET", "POST"])
def wechat():
    """验证服务器地址的有效性"""
    signature = request.args.get("signature")
    timestamp = request.args.get("timestamp")
    nonce = request.args.get("nonce")

    if not all([signature, timestamp, nonce]):
        # 抛出400错误
        abort(400)

    li = [WECHAT_TOKEN, timestamp, nonce]
    li.sort()
    tmp_str = "".join(li)
    tmp_str = tmp_str.encode('utf-8')
    sign = hashlib.sha1(tmp_str).hexdigest()
    if signature != sign:
        # 请求不是来自微信，弹出报错信息, 身份有问题
        abort(403)
    
    # 表示是微信发送的请求,第一次接入微信服务器的验证时才会使用
    if request.method == "GET":
        echostr = request.args.get("echostr")
        if not echostr:
            abort(400)
        return echostr

    if request.method == "POST":
        xml_str = request.data
        
        # 当xml_str为空时
        if not xml_str:
            abort(400)

        # 将xml字符串解析成字典
        xml_dict = xmltodict.parse(xml_str)
        xml_dict = xml_dict.get("xml")
        logger.info(xml_dict.get("FromUserName"))
        return wechat_message(xml_dict)

def wechat_message_image(xml_dict):
    async def async_handle():
        # 下载图片，以时间命名，为了确保图片文件名的唯一性，时间精确到纳秒(10^-6秒)，例如：2022-12-03-165018047661.png
        filename = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S%f")+".png"
        r = requests.get(xml_dict.get("PicUrl"))
        with open(filename, 'wb') as f:
            f.write(r.content)
        # 上传
        picurl = upload_file(githubuser,filename)
        # 将图片链接改成markdown中的表达形式
        body = "<img width=200 src=\"{}\" alt=\"{}\" />".format(picurl,filename)
        # 发布issue
        title = time.strftime('%Y年%m月%d日 %H:%M:%S',time.localtime(time.time()))
        message = create_github_issue(githubuser,title,body)
        logger.info(message)

    asyncio.run_coroutine_threadsafe(async_handle(),thread_loop)
    # 告知用户issue是否成功发布
    resp_dict = {
        "xml":{
            "ToUserName":xml_dict.get("FromUserName"),
            "FromUserName":xml_dict.get("ToUserName"),
            "CreateTime":int(time.time()),
            "MsgType":"text",
            "Content":"OK"
        }
    }
    return resp_dict

def wechat_message_text(xml_dict):
    # 发布GitHub issue
    title = time.strftime('%Y年%m月%d日 %H:%M:%S',time.localtime(time.time()))
    body = xml_dict.get("Content")
    
    if WECHAT_REGISTER == body[0:4] and len(body) == 16:
        # 绑定微信ID和GitHub Identity
        identity = body[4:16]
        wechat_id = xml_dict.get("FromUserName")
        # 查找数据库中的 wechat_id, 如果有，删去那条数据。
        # 查找数据库中的 identity, 更新其 wechat_id 条目。
        # 提交数据库。
        message = "成功绑定GitHub账号和微信账号"+body[4:16]
    else :
        message = create_github_issue(githubuser,title,body)

    # 返回消息告知用户issue是否成功发布
    resp_dict = {
        "xml":{
            "ToUserName":xml_dict.get("FromUserName"),
            "FromUserName":xml_dict.get("ToUserName"),
            "CreateTime":int(time.time()),
            "MsgType":"text",
            "Content":message
        }
    }
    return resp_dict

def wechat_message_video(xml_dict):
    access_token = wechat_access_token()
    # 下载视频文件
    baseurl = "https://api.weixin.qq.com/cgi-bin/media/get?"
    params = {
        "access_token" : access_token,
        "media_id" : xml_dict.get("MediaId")
    }
    filename = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S%f")+".mp4"
    r = requests.get(baseurl, params=params)
    with open(filename, 'wb') as f:
        f.write(r.content)
    
    video_url = upload_file(githubuser,filename)
    body = "<video src={} width=200 controls></video>".format(video_url)
    # 发布issue
    title = time.strftime('%Y年%m月%d日 %H:%M:%S',time.localtime(time.time()))
    message = create_github_issue(githubuser,title,body)
    # 告知用户issue是否成功发布
    resp_dict = {
        "xml":{
            "ToUserName":xml_dict.get("FromUserName"),
            "FromUserName":xml_dict.get("ToUserName"),
            "CreateTime":int(time.time()),
            "MsgType":"text",
            "Content":message
        }
    }
    return resp_dict

def wechat_message(xml_dict):
    # MsgType是消息类型 这里提取消息类型
    msg_type = xml_dict.get("MsgType")

    if msg_type == "text":
        resp_dict = wechat_message_text(xml_dict)

    elif msg_type == "image":
        resp_dict = wechat_message_image(xml_dict)

    elif msg_type == "video":
        resp_dict = wechat_message_video(xml_dict)
    
    else:
        resp_dict = {
            "xml": {
                "ToUserName": xml_dict.get("FromUserName"),
                "FromUserName": xml_dict.get("ToUserName"),
                "CreateTime": int(time.time()),
                "MsgType": "text",
                "Content": "不能处理消息类型：" + msg_type
            }
        }
    # 将字典转换为xml字符串
    resp_xml_str = xmltodict.unparse(resp_dict)
    logger.info(resp_dict)
    logger.info(resp_xml_str)
    # 返回消息数据给微信服务器
    return resp_xml_str

def wechat_access_token():
    # 获取微信的access token，在获取音频和视频文件时用得到
    # 注意：虽然官方文档有向用户发送视频文件的方法，但本人多次尝试无法成功。有人询问过微信官方，但是微信官方不置可否。
    baseurl = "https://api.weixin.qq.com/cgi-bin/token?"
    params = {
        "grant_type":"client_credential",
        "appid": WECHAT_APPID,         
        "secret": WECHAT_SECRET
    }
    r = requests.get(baseurl, params=params)
    print(r)
    access_token = r.json()["access_token"]
    try:
        r = requests.get(baseurl, params=params)
    except Exception as e:
        print(e)
    return access_token


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

# sudo python3 wechat.py
