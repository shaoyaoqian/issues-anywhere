# issues-anywhere

### 前言
什么是IA(Issues Anywhere) Talk ？
IA talk利用手机微信发布碎片化思想同步至博客，基于GitHub Issues，无需任何后端服务。

### 特性
支持微信端文字及图片消息发送
当前为初步版本，后续功能请见开发计划

### 原理
<img width="768" alt="image" src="https://user-images.githubusercontent.com/115222128/208239045-d8d9e4c8-0507-4701-8e6d-f4a696df3bb6.png">
详细内容参见我博客https://blog.pengfeima.cn/posts/14811/
以及讨论：https://github.com/xaoxuu/hexo-theme-stellar/issues/199

### 支持
目前仅支持在 Hexo Stellar 主题使用，通过timeline插件插入文档。
```
{% timeline user:[用户名] api:https://api.github.com/repos/[用户名]/[仓库名]/issues %}
{% endtimeline %}
```
效果如下：

![](https://user-images.githubusercontent.com/115222128/208243727-a5ba4f6f-703c-41d0-a843-021a137fcdd2.png)

### 快速开始
#### 安装GitHub App
新建一个GitHub仓库，安装应用[wechat-to-issues](https://github.com/apps/wechat-to-issues)，只授权你刚创建的仓库。
![](https://user-images.githubusercontent.com/115222128/208220300-d7cf13ef-aa09-41e6-8adf-25fdde17ec1b.png)
#### 关注公众号

#### 绑定仓库
然后再向公众号发送 di3a仓库名，前缀di3a是指令名。举个例子，我的仓库是blog，我就发送di3ablog，首尾不能有空格。

### 在博客正文中插入
```
{% timeline user:[用户名] api:https://api.github.com/repos/[用户名]/[仓库名]/issues %}
{% endtimeline %}
```




文档撰写参考了[BBTALK](https://bb.js.org/quick-start.html)，下面这些是草稿，先不要看。

📲随时发送
拿出手机即可发送碎片化思想，并同步博客显示。

🤞使用方便
简略的 html 片段即可实现，且理论上支持任何框架或单独页面。

🎁操作简单
微信端直接发送文字、图片、视频。

🤖无需后台
有一个微信账号和一个GitHub账号即可使用功能。


支持微信端文字及图片消息发送
当前为初步版本，后续功能请见开发计划







                # 流程：
                # 登陆GitHub，提供 GitHub identity、username、access token
                # 绑定微信，提供 wechat id
                # 设置 issue_repository
                # 设置 data_repository
                
使用方法：

1. 点击下面这个链接，登陆你的GitHub账号，必须登陆使用，我必须以某个身份发issue。（其实匿名也可以，用我的身份发issue，可以吗？）
https://github.com/login/oauth/authorize?client_id=Iv1.d5df482df1cd3635
<img width="486" alt="image" src="https://user-images.githubusercontent.com/115222128/208010029-ea0565a4-0195-4b6e-95b0-a0b51018ec13.png">
<img width="740" alt="image" src="https://user-images.githubusercontent.com/115222128/208005737-020b8057-addb-4baf-a223-a30ee6f14a0a.png">

2. 到微信公众号，将你的绑定这个GitHub账号
<img width="479" alt="image" src="https://user-images.githubusercontent.com/115222128/208007132-a8454dd1-b939-4458-961b-854c9c586aa5.png">

3. 此时你往公众号发的消息将同步到公共仓库的issues中，不过你可以绑定你自己的仓库
<img width="480" alt="image" src="https://user-images.githubusercontent.com/115222128/208008916-0cf34ce5-895d-4a71-b935-690d90fa7bd6.png">

4. 图片、视频、语音消息无法发送到公共仓库，必须要向app授权自己的仓库
<img width="473" alt="image" src="https://user-images.githubusercontent.com/115222128/208009741-8c460fa2-cd69-4a54-b7b6-6296d16dc2ea.png">

5. 看效果
https://blog.pengfeima.cn/about/


<img width="489" alt="image" src="https://user-images.githubusercontent.com/115222128/208011770-6c99a7e6-bbea-4a01-b126-ffdaa0d2e2ed.png">

<img width="345" alt="image" src="https://user-images.githubusercontent.com/115222128/208011866-97d6271c-daff-4434-8fd8-a453e214d52a.png">

6. 其实很多部分还没写完，我恨，我没有那么多时间～



这个程序写了整整三天了，还不包括前阵子写好的那部分，唉～

