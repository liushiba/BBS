# -* coding: utf-8 -*-

from tornado import gen

from database.sql_utils.connect import async_connect


@gen.coroutine
def get_user_by_username(username):  # 获取用户名
    conn = yield async_connect()
    cur = conn.cursor()
    sql = "SELECT username, email, password FROM t_user WHERE username='%s';" % username
    try:
        yield cur.execute(sql)
        data = cur.fetchone()
    except Exception as e:
        data = {}
    finally:
        cur.close()
        conn.close()
    raise gen.Return(data)


@gen.coroutine
def create_user(username, password):  # 创建用户
    conn = yield async_connect()
    cur = conn.cursor()
    sql = "INSERT INTO t_user(username, password) VALUES ('%s', '%s');" % (username, password)
    try:
        data = yield cur.execute(sql)
    except Exception as e:
        data = 0
    finally:
        cur.close()
        conn.close()
    raise gen.Return(data)


@gen.coroutine
def get_group_by_user(username):  # 获取用户组
    conn = yield async_connect()
    cur = conn.cursor()
    sql = "SELECT group_type FROM t_user WHERE username='%s'"  % username
    try:
        yield cur.execute(sql)
        data = cur.fetchone()
    except Exception as e:
        data = None
    finally:
        cur.close()
        conn.close()
    raise gen.Return(data)