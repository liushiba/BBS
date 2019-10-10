# -*- coding: utf-8 -*-

from tornado import gen

from database.tornado_mysql import escape_string
from database.sql_utils.connect import async_connect


@gen.coroutine
def get_answers(qid):  # 获取答案列表
    conn = yield async_connect()
    cur = conn.cursor()
    sql = "SELECT a.aid, a.status, a.created_at, a.updated_at, a.content, u.username FROM t_answer a LEFT JOIN t_user u ON u.uid=a.uid WHERE qid=%d ORDER BY a.created_at ASC;" % qid
    try:
        yield cur.execute(sql)
        data = cur.fetchall()
    except Exception as e:
        data = []
    finally:
        cur.close()
        conn.close()
    raise gen.Return(data)


@gen.coroutine
def get_answer_status(user):  # 获取答案状态
    conn = yield async_connect()
    cur = conn.cursor()
    sql = "SELECT SUM(c) AS answer_count FROM (SELECT qid, COUNT(qid) AS c FROM t_answer WHERE has_read=0 GROUP BY qid) AS a WHERE a.qid IN (SELECT qid FROM t_question WHERE uid=(SELECT uid FROM t_user WHERE username='%s'));" % user
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
def create_answer(qid, user, content):  # 创建答案
    conn = yield  async_connect()
    cur = conn.cursor()
    if isinstance(content, str):
        content = escape_string(content)

    sql1 = "INSERT INTO t_answer (qid, uid, content) VALUES (%d, (SELECT uid FROM t_user WHERE username='%s'), '%s');" % (qid, user, content)
    sql2 = "UPDATE t_question SET answer_count = answer_count + 1 WHERE qid=%d;" % qid
    try:
        data = yield cur.execute(sql1)
        yield cur.execute(sql2)
    except Exception as e:
        data = 0
    finally:
        cur.close()
        conn.close()
    raise gen.Return(data)


@gen.coroutine
def get_unread_answer(user):  # 获取未读答案
    conn = yield async_connect()
    cur = conn.cursor()
    # sql = "SELECT q.qid, q.abstract, u.username FROM t_answer a LEFT JOIN t_question q ON a.qid = q.qid LEFT JOIN t_user u ON u.uid = a.uid WHERE q.uid = (SELECT uid FROM t_user WHERE username='%s');" % user
    sql = "SELECT a.qid, a.answer_count, c.abstract FROM "
    sql += "(SELECT qid, COUNT(qid) AS answer_count FROM t_answer WHERE has_read=0 GROUP BY qid) AS a"
    sql += " LEFT JOIN t_question AS c ON c.qid = a.qid WHERE a.qid IN (SELECT b.qid FROM t_question AS b"
    sql += " WHERE uid=(SELECT uid FROM t_user WHERE username='%s'));" % user
    try:
        yield cur.execute(sql)
        data = cur.fetchall()
    except Exception as e:
        data = []
    finally:
        cur.close()
        conn.close()
    raise gen.Return(data)


@gen.coroutine
def check_answers(qid):  # 更新未读答案
    conn = yield async_connect()
    cur = conn.cursor()
    sql = "UPDATE t_answer SET has_read=1 WHERE qid=%d" % qid
    try:
        data = yield cur.execute(sql)
    except Exception as e:
        data = 0
    finally:
        cur.close()
        conn.close()
    raise gen.Return(data)


@gen.coroutine
def delete_answer_by_id(aid, qid, user):  # 删除答案
    conn = yield async_connect()
    cur = conn.cursor()
    sql = "DELETE FROM t_answer WHERE aid = %d AND qid = %d AND uid=(SELECT uid FROM t_user WHERE username='%s');" % (aid, qid, user)
    try:
        result = yield cur.execute(sql)
    except Exception as e:
        result = 0
    raise gen.Return(result)


@gen.coroutine
def adopt_answer(aid, qid):  # 采纳答案
    conn = yield async_connect()
    cur = conn.cursor()
    sql = "UPDATE t_answer SET status=TRUE WHERE aid=%d AND qid=(SELECT qid FROM t_question WHERE qid=%d);" % (aid, qid)
    try:
        data = yield cur.execute(sql)
    except Exception as e:
        data = 0
    finally:
        cur.close()
        conn.close()
    raise gen.Return(data)


@gen.coroutine
def add_point(aid, qid, user):  # 增加得分
    conn = yield async_connect()
    cur = conn.cursor()
    sql1 = "UPDATE t_user SET point = point + 1 WHERE uid = (SELECT uid FROM t_answer WHERE aid=%d AND qid=%d);" % (aid, qid)
    sql2 = "UPDATE t_question SET status=TRUE, adopted_count = adopted_count + 1 WHERE qid = %d AND uid = (SELECT uid FROM t_user WHERE username='%s');" % (qid, user)
    try:
        data1 = yield cur.execute(sql1)
        data2 = yield cur.execute(sql2)
        data = data1 and data2
    except Exception as e:
        data = 0
    finally:
        cur.close()
        conn.close()
    raise gen.Return(data)


@gen.coroutine
def get_adopted_count(qid, user):  # 获取得分数据
    conn = yield async_connect()
    cur = conn.cursor()
    sql = "SELECT adopted_count FROM t_question WHERE qid=%d AND uid=(SELECT uid FROM t_user WHERE username='%s')" % (qid, user)
    try:
        yield cur.execute(sql)
        data = cur.fetchone()
    except Exception as e:
        data = {}
    finally:
        cur.close()
        conn.close()
    raise gen.Return(data)