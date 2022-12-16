
import time
import jwt  #需要安装pip install pyjwt

key = open("we.pem",'r').read()
print(key)

def generate_token():
    """
     :param user: 用户对象
     :return: 生成的token
    """
    #自己组织payload
    payload = {
        'iat': int(time.time())-100,
        'exp': int(time.time())+500,
        'iss': "272667"
    }
    token = jwt.encode(payload=payload, key=key, algorithm='RS256')
    return token

print(generate_token())

# TOKEN 的使用

# python程序生成的token和ruby程序生成的token不一样

# curl -i -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2NzEwOTA4NjksImV4cCI6MTY3MTA5MTQ2OSwiaXNzIjoiMjcyNjY3In0.y5CQ2AmzK88kZLYI4pJ4q1z-hTcmA8-C_MWw6W7mIix773tqP1YXUHyh3GW3YlhlrGkuEsa-dGZXbgwHD8Tgk7-rZOQPQ_Jgmlw8MXwDwFoXboEL5JXUGzYaha6kgyuHBiLza40jzYmBcud4021BVXPQN_GVlrU1pYNCvtiNOccXWghme2AfHbiCFZuVbeUDnUXO7GIMwUDRLqTN79PB9npGODuoaxf6gYf1i3P-sUwUmXSwMdzmVxSpNsTB2N-3bYneS5lTU1E9cjI6vpYCgYznZ_8dD0_M6k9F8mRIeTQPYlAWCNeibel-xJgfssNK13SK6vcqidetwhEX-V6G1Q" -H "Accept: application/vnd.github+json" https://api.github.com/app
# 文档：https://docs.github.com/en/rest/apps/apps?apiVersion=2022-11-28#create-an-installation-access-token-for-an-app

# 获取 access token
# curl -i -X POST -H "Authorization: Bearer YOUR_JWT" -H "Accept: application/vnd.github+json" https://api.github.com/app/installations/{installation_id}/access_tokens 
# 文档


# curl -i -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2NzEwOTA4NjksImV4cCI6MTY3MTA5MTQ2OSwiaXNzIjoiMjcyNjY3In0.y5CQ2AmzK88kZLYI4pJ4q1z-hTcmA8-C_MWw6W7mIix773tqP1YXUHyh3GW3YlhlrGkuEsa-dGZXbgwHD8Tgk7-rZOQPQ_Jgmlw8MXwDwFoXboEL5JXUGzYaha6kgyuHBiLza40jzYmBcud4021BVXPQN_GVlrU1pYNCvtiNOccXWghme2AfHbiCFZuVbeUDnUXO7GIMwUDRLqTN79PB9npGODuoaxf6gYf1i3P-sUwUmXSwMdzmVxSpNsTB2N-3bYneS5lTU1E9cjI6vpYCgYznZ_8dD0_M6k9F8mRIeTQPYlAWCNeibel-xJgfssNK13SK6vcqidetwhEX-V6G1Q" -H "Accept: application/vnd.github+json" https://api.github.com/app
