# -*- coding: utf-8 -*-

import json

from tornado import gen
from tornado import web

from handlers.base_handlers import BaseHandler
from database.sql_utils.question import update_question_answer
from database.sql_utils.answer import (get_answers, create_answer, get_answer_status, get_unread_answer, check_answers,
                                       delete_answer_by_id, adopt_answer, add_point, get_adopted_count)
from database.nosql_utils.connect import redis_connect
from database.nosql_utils.channels import ANSWER_STATUS_CHANNEL

from utils.errcode import PARAMETER_ERR, CREATE_ERR, USER_HAS_NOT_VALIDATE, DEL_ERR, ADD_POINT_ERR, ADOPT_COUNT_ERR
from utils.jsonEncoder import JsonEncoder
from utils.auth import login_required


class AnswerListHandler(BaseHandler):
    """
    答案列表控制器
    """
    @gen.coroutine
    def get(self, qid, *args, **kwargs):  # 渲染数据
        try:
            qid = int(qid) # 将qid转化为整型
        except Exception as e: # 异常处理
            self.json_response(*PARAMETER_ERR)
            raise gen.Return()
        data = yield get_answers(qid)  # 获取答案列表
        yield check_answers(qid)  # 更新未读答案
        # 返回Json格式数据
        self.json_response(200, 'OK', {
            'answer_list': data,
        })


class AnswerCreateHandler(BaseHandler):
    """
    创建答案控制器
    """
    def initialize(self):             # 初始化redis数据库
        self.redis = redis_connect()  # 配置redis
        self.redis.connect()          # 连接redis

    @gen.coroutine
    @login_required
    def post(self, *args, **kwargs):  # 提交数据
        qid = self.get_argument('qid', '') # 获取qid参数，默认为空
        content = self.get_argument('content', '') # 获取content参数，默认为空
        user = self.current_user # 将当前用户信息赋值给user变量

        try:
            qid = int(qid) # 将qid转化为整型
        except Exception as e: # 异常处理
            self.json_response(*PARAMETER_ERR)
            raise gen.Return()

        if not user: # 如果用户不存在，返回错误信息
            self.json_response(*USER_HAS_NOT_VALIDATE)
            raise gen.Return()
        data = yield create_answer(qid, user, content) # 创建答案
        answer_status = yield get_answer_status(user)  # 获取答案状态

        if not data: # 如果创建答案不存在，提示创建失败
            self.json_response(*CREATE_ERR)
            raise gen.Return()
        yield gen.Task(self.redis.publish, ANSWER_STATUS_CHANNEL, json.dumps(answer_status, cls=JsonEncoder))  # 更新到channel
        self.json_response(200, 'OK', {}) # 返回Json数据


class AnswerDetailHandler(BaseHandler):
    def get(self, *args, **kwargs):
        pass

    def post(self, *args, **kwargs):
        pass


class AnswerUpdateHandler(BaseHandler):
    def get(self, *args, **kwargs):
        pass

    def post(self, *args, **kwargs):
        pass


class AnswerDeleteHandler(BaseHandler):
    """
    删除问题控制器
    """
    def get(self, *args, **kwargs):
        pass

    @gen.coroutine
    @login_required
    def post(self, aid, *args, **kwargs):  # 提交数据
        qid = self.get_argument('qid', '')
        try:
            qid = int(qid)
        except Exception as e:
            self.json_response(*PARAMETER_ERR)
            raise gen.Return()
        try:
            aid = int(aid)
        except Exception as e:
            self.json_response(*PARAMETER_ERR)
            raise gen.Return()

        user = self.current_user
        result = yield delete_answer_by_id(aid, qid, user)
        up_result = yield update_question_answer(qid)
        if (not result) or (not up_result):
            self.json_response(*DEL_ERR)
            raise gen.Return()
        self.json_response(200, 'OK', {})


class AnswerStatusHandler(BaseHandler):
    """
    答案状态长轮询控制器
    """
    def initialize(self):  # 初始化redis数据库
        self.redis = redis_connect()
        self.redis.connect()

    @web.asynchronous
    def get(self, *args, **kwargs):  # 请求到来订阅到redis
        if self.request.connection.stream.closed():
            raise gen.Return()
        self.register()  # 注册回调函数

    @gen.engine
    def register(self):  # 订阅消息
        yield gen.Task(self.redis.subscribe, ANSWER_STATUS_CHANNEL)
        self.redis.listen(self.on_response)

    def on_response(self, data):  # 响应到来返回数据
        if data.kind == 'message':  # 类型为消息
            try:
                self.write(data.body)
                self.finish()
            except Exception as e:
                pass
        elif data.kind == 'unsubscribe':  # 类型为取消订阅
            self.redis.disconnect()

    def on_connection_close(self):  # 关闭连接
        self.finish()


class AnswerStatusCurrentHandler(BaseHandler):
    """
    答案当前状态控制器
    """
    @gen.coroutine
    def get(self, *args, **kwargs):  # 获取当前用户
        data = yield get_answer_status(self.current_user)
        self.json_response(200, 'OK', data)


class UnreadAnswerHandler(BaseHandler):
    """
    未读消息控制器
    """
    @gen.coroutine
    @login_required
    def get(self, *args, **kwargs):  # 渲染页面
        user = self.current_user
        uquestions = yield get_unread_answer(user)
        self.render('unread_answer.html', data={'unread_questions': uquestions})


class AnswerAdoptHandler(BaseHandler):
    """
    采纳答案控制器
    """
    @gen.coroutine
    @login_required
    def post(self, aid, *args, **kwargs):  # 提交数据
        qid = self.get_argument('qid', '')
        user = self.current_user

        try:
            aid = int(aid)
        except Exception as e:
            self.json_response(*PARAMETER_ERR)
            raise gen.Return()
        try:
            qid = int(qid)
        except Exception as e:
            self.json_response(*PARAMETER_ERR)
            raise gen.Return()

        adopted_data = yield get_adopted_count(qid, user)
        if adopted_data.get('adopted_count', 0) >= 3:
            self.json_response(*ADOPT_COUNT_ERR)
            raise gen.Return()

        data = yield adopt_answer(aid, qid)
        if not data:
            self.json_response(*CREATE_ERR)
            raise gen.Return()

        data_point = yield add_point(aid, qid, user)
        if not data_point:
            self.json_response(*ADD_POINT_ERR)
            raise gen.Return()

        self.json_response(200, 'OK', {})
