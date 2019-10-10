# -*- coding: utf-8 -*-

from tornado import gen

from handlers.base_handlers import BaseHandler

from database.sql_utils.user import get_user_list, get_user_by_str

from utils.auth import login_required
from utils.errcode import PARAMETER_ERR


class UserListHandler(BaseHandler):
    """
    用户列表控制器
    """
    @gen.coroutine
    @login_required
    def get(self, *args, **kwargs):  # 渲染页面
        data = yield get_user_list()
        my_data = {}
        if data:
            for i in data:
                if i.get('username') == self.current_user:
                    my_data = {'username': i.get('username'), 'point': i.get('point'), 'rank': i.get('ranks') }
        self.render('user_list.html', data={
            'user_list': data,
            'current_user': my_data
        })


class UserSearchHandler(BaseHandler):
    """
    用户搜索控制器
    """
    @gen.coroutine
    @login_required
    def get(self, *args, **kwargs):  # 搜索
        s = self.get_argument('s', '')
        if not 2 <= len(s) <= 12:
            self.json_response(*PARAMETER_ERR)
            raise gen.Return()

        data = yield get_user_by_str(s)
        self.json_response(200, 'OK', data={'user_list': data})