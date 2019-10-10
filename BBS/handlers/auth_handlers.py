# -*- coding: utf-8 -*-

import base64
import uuid
import hashlib
from urllib import parse
from io import BytesIO

from tornado import gen

from handlers.base_handlers import BaseHandler
from database.sql_utils.auth import get_user_by_username, create_user

from utils.auth_code import get_pic_code
from utils.logger import logger
from utils.errcode import LOGIN_VCODE_ERR, PASSWORD_ERR, USERNAME_ERR, USER_EXISTS, USER_CREATE_ERR


class LoginHandler(BaseHandler):
    """登录控制器"""
    @gen.coroutine
    def get(self, *args, **kwargs):  # 渲染页面
        self.render('login.html')

    @gen.coroutine
    def post(self, *args, **kwargs):  # 登录数据提交
        sign = self.get_argument('sign', '')            # 接收验证码标识参数
        vcode = self.get_argument('vcode', '')          # 接收验证码参数
        username = self.get_argument('username', '')    # 接收用户名参数
        password = self.get_argument('password', '')    # 接收密码参数
        # 检测验证码是否正确
        if self.get_secure_cookie(sign).decode('utf-8') != vcode:  # 如果验证码错误
            self.json_response(*LOGIN_VCODE_ERR)                   # 返回json格式的错误提示
            raise gen.Return()

        data = yield get_user_by_username(username)   # 根据用户名获取数据
        if not data:                                  # 如果用户名不存在
            self.json_response(*USERNAME_ERR)          # 提示错误信息
            raise gen.Return()
        # 检测密码是否正确
        if data.get('password') != hashlib.sha1(password.encode('utf-8')).hexdigest():  # 如果密码错误
            self.json_response(*PASSWORD_ERR)                                           # 返回json格式错误信息
            raise gen.Return()

        self.set_secure_cookie('auth-user', data.get('username', ''))           # 设置Cookie
        self.set_cookie('username', data.get('username', ''), expires_days=30)  # 设置过期时间为30天
        self.json_response(200, 'OK', {})


class LogoutHandler(BaseHandler):
    """
    登出控制器
    """
    @gen.coroutine
    def get(self, *args, **kwargs):
        next = self.get_argument('next', '') # 获取next参数
        self.clear_cookie('auth-user')       # 删除auth_user的Cookie值
        self.clear_cookie('username')       #  删除username的Cookie值
        next = next + '?' + parse.urlencode({'m': '注销成功', 'e': 'success'}) # 拼接URL参数
        self.redirect(next) # 跳转到注销页面


class SignupHandler(BaseHandler):
    """
    注册控制器
    """
    @gen.coroutine
    def get(self, *args, **kwargs):  # 渲染页面
        self.render('login.html')

    @gen.coroutine
    def post(self, *args, **kwargs):                 # 提交注册数据
        username = self.get_argument('username', '') # 接收用户名参数
        password = self.get_argument('password', '') # 接收密码参数
        vcode = self.get_argument('vcode', '') # 接收验证码参数
        sign = self.get_argument('sign', '')   # 接收验证码标识参数
        # 检测验证码是否正确
        if self.get_secure_cookie(sign).decode('utf-8') != vcode:
            self.json_response(*LOGIN_VCODE_ERR)
            raise gen.Return()

        data = yield get_user_by_username(username) # 根据用户名获取用户信息
        if data: # 如果用户已经存在
            self.json_response(*USER_EXISTS) # 提示错误信息
            raise gen.Return()

        password = hashlib.sha1(password.encode('utf-8')).hexdigest()  # 加密密码
        result = yield create_user(username, password) # 将用户名和密码写入数据库
        if not result: # 如果结果不存在，提示错误信息
            self.json_response(*USER_CREATE_ERR)
            raise gen.Return()

        self.set_secure_cookie('auth-user', username)          # 生成登录cookie
        self.set_cookie('username', username, expires_days=30) # 设置过期时间
        self.json_response(200, 'OK', {})


class AuthCodeHandler(BaseHandler):
    """
    验证码控制器
    """
    @gen.coroutine
    def get(self, *args, **kwargs): # 获取验证码
        b = BytesIO()
        img, check = yield get_pic_code()
        img.save(b, format='png')
        vcode = base64.b64encode(b.getvalue())
        sign = str(uuid.uuid1())
        self.set_secure_cookie(sign, ''.join([str(i) for i in check]).lower(), expires_days=1/48)
        self.json_response(200, 'OK', {
            'vcode': vcode.decode('utf-8'),
            'sign': sign
        })
