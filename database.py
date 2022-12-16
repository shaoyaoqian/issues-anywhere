# sqlite 数据库的一些基本操作 https://zhuanlan.zhihu.com/p/407131061

import sqlite3

def init_database(path='test.sqlite'):
    # 数据库代码
    connection = sqlite3.connect(path)
    curs = connection.cursor()
    create_database(connection)
    return connection, curs

def create_database(connection):
    CREATE_TABLE = '''
    CREATE TABLE IF NOT EXISTS
        user1 (
        identity        int,
        access_token    TEXT,
        refresh_token   TEXT,
        installation_id TEXT,
        wechat_id       TEXT,
        username        TEXT,
        repository      TEXT,
        image_repository TEXT
    )
    '''
    connection.execute(CREATE_TABLE)


connection, curs = init_database()

# 数据库参数
INSERT = "INSERT INTO user1 (identity, access_token) VALUES ('1', '0')"
curs.execute(INSERT)

connection.commit()


SELECT_ID = "SELECT identity, access_token, refresh_token, installation_id, wechat_id, username, repository from user1 where identity=1"
result = curs.execute(SELECT_ID)

print(result.arraysize)

for row in result:
    print(row)

SELECT_STATUS = "SELECT id, status from MOVIE where status={status:d}"
UPDATE = "UPDATE MOVIE set status = 1 where ID={id:d}"



# 关闭游标
curs.close()
# 断开数据库连接
connection.close()