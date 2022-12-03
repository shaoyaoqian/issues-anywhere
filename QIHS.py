from qiniu import Auth, put_file, etag
import qiniu.config
# 七牛
QINIU_ACCESS_KEY = "NLI1UowRkIZiebmdEZ7MWNDLtPYeqJWkc90MFn_0"
QINIU_SECRET_KEY = "NMgdo5YrD8zQhzc8ZGWH4t-pcGEeLOYzFYJZhiG-"
QINIU_CDN_BASE   = "https://china-qiniu-s3.pengfeima.cn/"
QINIU_BUCKET     = 'pengfei-npu'

# 上传到七牛云图床，参考：https://developer.qiniu.com/kodo/1242/python
# 默认存储到"blog/moments/"路径下
def upload_file(filename, path="blog/moments/"):
    #构建鉴权对象
    q = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
    #要上传的空间
    bucket_name = QINIU_BUCKET
    #要上传文件的本地路径
    localfile = filename
    #上传后保存的文件名
    key = path + filename
    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)
    ret, info = put_file(token, key, localfile, version='v2') 
    print(info)
    assert ret['key'] == key
    assert ret['hash'] == etag(localfile)
    return QINIU_CDN_BASE + key
