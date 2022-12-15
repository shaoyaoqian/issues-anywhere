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
from urllib.parse import parse_qs
from loguru import logger 

# GITHUB 模块
from GIHS import create_github_issue, user_access_token
from GIHS import GIHS_upload_file as upload_file
# from QIHS import upload_file

# 异步任务池
import asyncio, time, threading
#  运行事件循环， loop以参数的形式传递进来运行
def start_loop(thread_loop):
    asyncio.set_event_loop(thread_loop)
    thread_loop.run_forever()

# 获取一个事件循环
thread_loop = asyncio.new_event_loop()
# 将次事件循环运行在一个线程中，防止阻塞当前主线程，运行线程，同时协程事件循环也会运行
threading.Thread(target=start_loop,args=(thread_loop,)).start()

# 微信的token令牌，参数的获取可参考：https://qiniu.pengfeima.cn/typora/202212031457547.png
WECHAT_TOKEN = 'look_back_at_me'
WECHAT_APPID = "wxcc6a1b8adade3237",         
WECHAT_SECRET = "29b97cdfd439873420ecf78e8221fdea"

# WECHAT_COMMAND
WECHAT_REGISTER = "n92k"

# 创建一个 Flask 应用
app = Flask(__name__)

# 用户点击下面这个链接登陆，然后会跳转到这里，获取code，然后向 GitHub 申请 access token。
# url = "https://github.com/login/oauth/authorize?client_id=Iv1.d5df482df1cd3635"
@app.route("/github-auth/", methods=["GET", "POST"])
def github():
    # 获取GitHub传输来的数据
    code = request.args.get("code")
    # installation_id = request.args.get("installation_id")
    # setup_action = request.args.get("setup_action")
    # 处理数据，获取access_token
    access_token = user_access_token(code)
    identity = hashlib.md5(code.encode('utf8')).hexdigest()
    message = """
    欢迎使用issues-anywhere机器人！ <br><br>
    微信公众号途径：<br>
    &ensp;&ensp;请关注公众号：Donald-Trump <br>
    &ensp;&ensp;您在本站的ID为：{identity} <br>
    &ensp;&ensp;请在公众号发送字符串以绑定身份(首尾无空格): <br>
    &ensp;&ensp;2bb40dc6c:{identity}<br>
    若失效，请点击：https://github.com/login/oauth/authorize?client_id=Iv1.d5df482df1cd3635
    """
    print(access_token)
    return message.format(identity=identity[0:4])

@app.route("/", methods=["GET", "POST"])
def wechat():
    """验证服务器地址的有效性"""
    # 开发者提交信息后，微信服务器将发送GET请求到填写的服务器地址URL上，GET请求携带四个参数:
    # signature:微信加密, signature结合了开发者填写的token参数和请求中的timestamp参数 nonce参数
    # timestamp:时间戳(chuo这是拼音)
    # nonce:    随机数
    # echostr:  随机字符串
    # 接收微信服务器发送参数
    signature = request.args.get("signature")
    timestamp = request.args.get("timestamp")
    nonce = request.args.get("nonce")

    # 校验参数
    # 校验流程：
    # 将token、timestamp、nonce三个参数进行字典序排序
    # 将三个参数字符串拼接成一个字符串进行sha1加密
    # 开发者获得加密后的字符串可与signature对比，标识该请求来源于微信
    if not all([signature, timestamp, nonce]):
        # 抛出400错误
        abort(400)

    # 按照微信的流程计算签名
    li = [WECHAT_TOKEN, timestamp, nonce]
    # 排序
    li.sort()
    # 拼接字符串
    tmp_str = "".join(li)
    tmp_str = tmp_str.encode('utf-8')
    # 进行sha1加密, 得到正确的签名值
    sign = hashlib.sha1(tmp_str).hexdigest()
    # 将自己计算的签名值, 与请求的签名参数进行对比, 如果相同, 则证明请求来自微信
    if signature != sign:
        # 代表请求不是来自微信
        # 弹出报错信息, 身份有问题
        abort(403)
    else:
        # 表示是微信发送的请求,第一次接入微信服务器的验证时才会使用
        if request.method == "GET":
            echostr = request.args.get("echostr")
            # 校验echostr
            if not echostr:
                abort(400)
            return echostr

        elif request.method == "POST":
            # 表示微信服务器转发消息过来
            # 拿取xml的请求数据
            xml_str = request.data

            # 当xml_str为空时
            if not xml_str:
                abort(400)

            # 将xml字符串解析成字典
            xml_dict = xmltodict.parse(xml_str)
            xml_dict = xml_dict.get("xml")
            return wechat_message(xml_dict)

def wechat_message_image(xml_dict):
    # PicUrl  图片链接
    # MediaId 图片消息的媒体id，图片被归为临时素材，通过统一接口调用。
    # 
    # resp_dict = {
    #     "xml":{
    #         "ToUserName":xml_dict.get("FromUserName"),
    #         "FromUserName":xml_dict.get("ToUserName"),
    #         "CreateTime":int(time.time()),
    #         "MsgType":"image",
    #         "Image":{
    #             "MediaId":xml_dict.get("MediaId")
    #         }
    #     }
    # }
    #
    async def async_handle():
        # 下载图片，以时间命名，为了确保图片文件名的唯一性，时间精确到纳秒(10^-6秒)，例如：2022-12-03-165018047661.png
        filename = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S%f")+".png"
        r = requests.get(xml_dict.get("PicUrl"))
        with open(filename, 'wb') as f:
            f.write(r.content)
        # 上传
        picurl = upload_file(filename)
        # 将图片链接改成markdown中的表达形式
        body = "<img width=200 src=\"{}\" alt=\"{}\" />".format(picurl,filename)
        # 发布issue
        title = time.strftime('%Y年%m月%d日 %H:%M:%S',time.localtime(time.time()))

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
    # 表示收到文本消息
    # 构造xml格式的返回值,
    # 返回值会经由微信服务器回复给用户
    # 其中：
    # ToUsername: (必须传) 接收方账号(收到的OpenID)
    # FromUserName: (必须传) 开发者微信号
    # CreateTime: (必须传) 消息创建时间(整形)
    # MsgType: (必须传) 消息类型
    # Content: (必须传) 回复消息的内容(换行:在Content中能够换行, 微信客户端就支持换行显示)

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
        message = create_github_issue(title,body)

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
    
    video_url = upload_file(filename)
    body = "<video src={} width=200 controls></video>".format(video_url)
    # 发布issue
    title = time.strftime('%Y年%m月%d日 %H:%M:%S',time.localtime(time.time()))
    message = create_github_issue(title,body)
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
