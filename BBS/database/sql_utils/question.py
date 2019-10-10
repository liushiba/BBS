# -*- coding: utf-8 -*-

from tornado import gen

from database.tornado_mysql import escape_string
from database.sql_utils.connect import async_connect
from database.nosql_utils.connect import redis_connect


@gen.coroutine
def get_paged_questions(page_count=10, last_qid=None, pre=False):  # 获取问题列表
    conn = yield async_connect()
    cur = conn.cursor()
    if not pre:  # 前页
        if not last_qid:
            sql = "SELECT q.qid, q.abstract, q.content, q.view_count, q.answer_count, u.username, t.tag_name FROM t_question q LEFT JOIN t_user u ON q.uid=u.uid LEFT JOIN t_tag t ON q.tid=t.tid ORDER BY qid DESC LIMIT %d;" % page_count
        else:
            sql = "SELECT q.qid, q.abstract, q.content, q.view_count, q.answer_count, u.username, t.tag_name FROM t_question q LEFT JOIN t_user u ON q.uid=u.uid LEFT JOIN t_tag t ON q.tid=t.tid WHERE qid<%d ORDER BY qid DESC LIMIT %d;" % (last_qid, page_count)
    else:  # 后页
        if not last_qid:
            return []
        else:
            sql = "SELECT q.qid, q.abstract, q.content, q.view_count, q.answer_count, u.username, t.tag_name FROM t_question q LEFT JOIN t_user u ON q.uid=u.uid LEFT JOIN t_tag t ON q.tid=t.tid WHERE qid>=%d ORDER BY qid DESC LIMIT %d;" % (last_qid, page_count)

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
def get_filtered_questions(name, user=None, tag=None):  # 获取过滤问题列表
    conn = yield async_connect()
    cur = conn.cursor()
    if name == 'newest':
        sql = "SELECT q.qid, q.abstract, q.content, q.view_count, q.answer_count, u.username, t.tag_name FROM t_question q LEFT JOIN t_user u ON q.uid=u.uid LEFT JOIN t_tag t ON q.tid=t.tid ORDER BY q.created_at DESC LIMIT 15;"
    elif name == 'hotest':
        sql = "SELECT q.qid, q.abstract, q.content, q.view_count, q.answer_count, u.username, t.tag_name FROM t_question q LEFT JOIN t_user u ON q.uid=u.uid LEFT JOIN t_tag t ON q.tid=t.tid ORDER BY answer_count DESC LIMIT 15;"
    elif name == 'under':
        sql = "SELECT q.qid, q.abstract, q.content, q.view_count, q.answer_count, u.username, t.tag_name FROM t_question q LEFT JOIN t_user u ON q.uid=u.uid LEFT JOIN t_tag t ON q.tid=t.tid WHERE q.status=0 ORDER BY q.created_at DESC LIMIT 15;"
    elif name == 'hasdone':
        sql = "SELECT q.qid, q.abstract, q.content, q.view_count, q.answer_count, u.username, t.tag_name FROM t_question q LEFT JOIN t_user u ON q.uid=u.uid LEFT JOIN t_tag t ON q.tid=t.tid WHERE q.status=1 ORDER BY q.created_at DESC LIMIT 15;"
    elif name == 'prefer' and user:
        sql = "SELECT q.qid, q.abstract, q.content, q.view_count, q.answer_count, u.username, t.tag_name FROM t_question q"
        sql += " LEFT JOIN t_user u ON q.uid=u.uid"
        sql += " LEFT JOIN t_tag t ON q.tid=t.tid"
        sql += " WHERE q.tid = (SELECT tid FROM t_question WHERE uid = (SELECT uid FROM t_user WHERE username = '%s') GROUP BY tid ORDER BY COUNT(tid) DESC LIMIT 1)" % user
        sql += " ORDER BY q.created_at DESC LIMIT 15;"
    elif tag:
        sql = "SELECT q.qid, q.abstract, q.content, q.view_count, q.answer_count, u.username, t.tag_name FROM t_question q LEFT JOIN t_user u ON q.uid=u.uid LEFT JOIN t_tag t ON t.tid = q.tid WHERE q.tid=%d ORDER BY answer_count DESC LIMIT 15;" % tag
    else:
        raise gen.Return([])
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
def create_question(tid, username, abstract, content):  # 创建问题
    conn = yield async_connect()
    cur = conn.cursor()
    if isinstance(abstract, str):
        abstract = escape_string(abstract)
    if isinstance(content, str):
        content = escape_string(content)

    sql1 = "INSERT INTO t_question (abstract, content, uid, tid) VALUES ('%s', '%s', (SELECT uid FROM t_user WHERE username='%s'), %d);" % (abstract, content, username, tid)
    sql2 = "SELECT LAST_INSERT_ID() as qid FROM t_question;"
    try:
        data = yield cur.execute(sql1)
        yield cur.execute(sql2)
        last_insert = cur.fetchone()
    except Exception as e:
        data = 0
        last_insert = {}
    finally:
        cur.close()
        conn.close()
    raise gen.Return((data, last_insert.get('qid', None)))


@gen.coroutine
def get_question_by_qid(qid):  # 获取问题详情
    conn = yield async_connect()
    cur = conn.cursor()
    sql = "SELECT q.qid, q.abstract, q.content, q.view_count, q.answer_count, q.created_at, q.updated_at, u.username, t.tag_name FROM t_question AS q LEFT JOIN t_user as u ON u.uid=q.uid LEFT JOIN t_tag as t ON q.tid=t.tid WHERE qid=%d;" % qid
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
def get_question_by_str(s):  # 查询问题
    conn = yield async_connect()
    cur = conn.cursor()
    sql = "SELECT q.qid, q.abstract, q.view_count, q.answer_count, q.created_at, q.updated_at, u.username, t.tag_name FROM t_question AS q "
    sql += "LEFT JOIN t_user as u ON u.uid=q.uid LEFT JOIN t_tag as t ON q.tid=t.tid WHERE abstract LIKE BINARY '%{}%' OR content LIKE BINARY '%{}%';".format(s, s)
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
def check_user_has_read(user, qid):  # 获取未读信息
    redis = redis_connect()
    redis.connect()

    conn = yield async_connect()
    cur = conn.cursor()
    has_read = yield gen.Task(redis.sismember, 'user:has:read:%d' % qid, user)
    if has_read:
        data = 0
        raise gen.Return(data)
    redis.sadd('user:has:read:%d' % qid, user)
    sql = "UPDATE t_question SET view_count = view_count + 1 WHERE qid = %d" % qid
    try:
        data = yield cur.execute(sql)
    except Exception as e:
        data = 0
    finally:
        cur.close()
        conn.close()
    raise gen.Return(data)


@gen.coroutine
def update_question_answer(qid):  # 更新答案
    conn = yield async_connect()
    cur = conn.cursor()
    sql = "UPDATE t_question SET answer_count = answer_count - 1 WHERE qid = %d;" % qid
    try:
        data = yield cur.execute(sql)
    except Exception as e:
        data = 0
    finally:
        cur.close()
        conn.close()
    raise gen.Return(data)


@gen.coroutine
def delete_question_by_id(qid, user):  # 删除问题
    conn = yield async_connect()
    cur = conn.cursor()
    sql = "DELETE FROM t_question WHERE qid = %d AND uid = (SELECT uid FROM t_user WHERE username='%s')" % (qid, user)
    try:
        data = yield cur.execute(sql)
    except Exception as e:
        data = 0
    finally:
        cur.close()
        conn.close()
    raise gen.Return(data)