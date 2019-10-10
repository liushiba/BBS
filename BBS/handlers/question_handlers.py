# -*- coding: utf-8 -*-

import os
import time
import uuid
import json

from tornado import gen

from handlers.base_handlers import BaseHandler
from database.sql_utils.tag import get_all_tags
from database.sql_utils.question import (get_paged_questions, create_question, get_question_by_qid,
                                         get_question_by_str, check_user_has_read, get_filtered_questions, delete_question_by_id)

from utils.errcode import PARAMETER_ERR, CREATE_ERR
from utils.auth import login_required
from conf import DEFAULT_UPLOAD_PATH, DOMAIN


class QuestionListHandler(BaseHandler):
    """
    问题列表控制器
    """
    @gen.coroutine
    def get(self, *args, **kwargs): # 渲染问题列表
        last_qid = self.get_argument('lqid', None) # 接收lqid参数，默认为None
        pre = self.get_argument('pre', 0) # 接收pre参数，默认为0
        if last_qid: # 如果last_qid存在
            try:
                last_qid = int(last_qid) # 将其转化为整型
            except Exception:  # 异常处理,返回json 数据
                self.json_response(200, 'OK', {
                    'question_list': [],
                    'last_qid': None
                })
        pre = True if pre == '1' else False # 将pre转化为布尔型
        data = yield get_paged_questions(page_count=15, last_qid=last_qid, pre=pre) # 获取问题列表
        lqid = data[-1].get('qid') if data else None # 判断data是否存在，并获取数据赋值给lqid
        # 返回json数据
        self.json_response(200, 'OK', {
            'question_list': data,
            'last_qid': lqid,
        })


class QuestionCreateHandler(BaseHandler):
    """
    创建问题控制器
    """
    @login_required
    @gen.coroutine
    def get(self, *args, **kwargs):  # 渲染页面
        tags = yield get_all_tags()  # 获取所有tag信息
        self.render('question_create.html', data={'tags': tags}) # 渲染模板

    @login_required
    @gen.coroutine
    def post(self, *args, **kwargs):  # 提交数据
        tag_id = self.get_argument('tag_id', '') # 接收tag参数
        abstract = self.get_argument('abstract', '') # 接收abstract参数
        content = self.get_argument('content', '') # 接收content参数
        user = self.current_user # 获取当前用户信息

        try:
            tag_id = int(tag_id) # 将tag_id转化为整型
        except Exception as e: # 异常处理并返回
            self.json_response(*PARAMETER_ERR)
            raise gen.Return()

        data, qid = yield create_question(tag_id, user, abstract, content) # 创建所有问题列表

        if not data: # 如果问题列表不存在
            self.json_response(*CREATE_ERR) # 返回Json数据，并提示创建失败
            raise gen.Return()
        # 返回Json数据
        self.json_response(200, 'OK', {'qid': qid})


class QuestionUploadPicHandler(BaseHandler):
    """
    上传图片控制器
    """
    @login_required
    @gen.coroutine
    def get(self, *args, **kwargs):     # 渲染页面
        self.json_response(200, 'OK', {})

    @login_required
    @gen.coroutine
    def post(self, *args, **kwargs):  # 提交图片数据
        pics = self.request.files.get('pic', None) # 获取pic参数
        urls = []
        if not pics: # 如果pic参数不存在，提示错误信息并返回
            self.json_response(*PARAMETER_ERR)
            raise gen.Return()
        folder_name = time.strftime('%Y%m%d', time.localtime()) # 使用文件名
        folder = os.path.join(DEFAULT_UPLOAD_PATH, folder_name) # 拼接文件目录
        if not os.path.exists(folder):  # 如果目录不存在
            os.mkdir(folder)  # 创建目录
        for p in pics: # 遍历图片
            file_name = str(uuid.uuid4()) + p['filename'] # 拼接文件名
            with open(os.path.join(folder, file_name), 'wb+') as f:  # 以二进制方式打开文件
                f.write(p['body'])                                    # 写入文件，即保存图片
            web_pic_path = 'pics/' + folder_name + '/' + file_name    # 拼接路径
            urls.append(os.path.join(DOMAIN, web_pic_path))           # 追加到列表
        # 返回Json格式数据
        self.write(json.dumps({
            'success': True,
            'msg': 'OK',
            'file_path': urls
        }))


class QuestionDeleteHandler(BaseHandler):
    """
    删除问题控制器
    """
    def get(self, *args, **kwargs):
        pass

    @gen.coroutine
    @login_required
    def post(self, qid, *args, **kwargs): # 提交数据
        user = self.current_user
        try:
            qid = int(qid)
        except Exception as e:
            self.json_response(*PARAMETER_ERR)
            raise gen.Return()
        result = yield delete_question_by_id(qid, user)
        if not result:
            self.json_response(*CREATE_ERR)
            raise gen.Return()
        self.json_response(200, 'OK', {})


class QuestionUpdateHandler(BaseHandler):
    def get(self, *args, **kwargs):
        pass

    def post(self, *args, **kwargs):
        pass


class QuestionDetailHandler(BaseHandler):
    """
    问题详情控制器
    """
    @gen.coroutine
    def get(self, qid, *args, **kwargs):  # 渲染数据
        user = self.current_user # 获取当前用户信息
        try:
            qid = int(qid) # 将qid转化为整型
        except Exception as e:  # 异常处理并返回
            self.json_response(*PARAMETER_ERR)
            raise gen.Return()
        if user: # 如果用户信息存在
            yield check_user_has_read(user, qid) # 获取未读信息

        data = yield get_question_by_qid(qid) # 获取问题详情
        self.render('question_detail.html', data={'question': data}) # 渲染页面


class QuestionSearchHandler(BaseHandler):
    """
    问题搜索控制器
    """
    @gen.coroutine
    def get(self, *args, **kwargs):  # 搜索
        s = self.get_argument('s', '')
        if not 3 < len(s) < 14:
            self.render('search_result.html', data={'result': [], 'msg': '参数不符合要求！'})
            raise gen.Return()
        data = yield get_question_by_str(s)
        self.render('search_result.html', data={'result': data, 'msg': ''})


class QuestionFilterHandler(BaseHandler):
    """
    问题过滤控制器
    """
    @gen.coroutine
    def get(self, name='', *args, **kwargs):  # 渲染数据
        if name in ['newest', 'hotest', 'under', 'hasdone', 'prefer']:
            data = yield get_filtered_questions(name, user=self.current_user)
        elif name.startswith('t_'):
            try:
                tid = int(name.split('_')[1])
            except Exception as e:
                self.json_response(*PARAMETER_ERR)
                raise gen.Return()
            data = yield get_filtered_questions(name, user=self.current_user, tag=tid)
        else:
            self.json_response(*PARAMETER_ERR)
            raise gen.Return()

        self.json_response(200, 'OK', data={'question_list': data})
