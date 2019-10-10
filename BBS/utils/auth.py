# -*- coding: utf-8 -*-

import functools

import urllib.parse as urlparse
from urllib.parse import urlencode

from tornado.web import HTTPError

from database.sql_utils.auth import get_group_by_user


def login_required(method):  # 登录装饰器
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        current_user = self.current_user
        if not current_user:
            if self.request.method in ("GET", "HEAD"):
                url = self.get_login_url()
                if "?" not in url:
                    if urlparse.urlsplit(url).scheme:
                        # if login url is absolute, make next absolute too
                        next_url = self.request.full_url()
                    else:
                        next_url = self.request.uri
                    url += "?" + urlencode(dict(next=next_url))
                self.redirect(url)
                return
            raise HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper


def admin_required(method):  # 管理员登录装饰器
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        current_user = self.current_user
        if not self.current_user:
            if self.request.method in ("GET", "HEAD"):
                url = self.get_login_url()
                if "?" not in url:
                    if urlparse.urlsplit(url).scheme:
                        # if login url is absolute, make next absolute too
                        next_url = self.request.full_url()
                    else:
                        next_url = self.request.uri
                    url += "?" + urlencode(dict(next=next_url))
                self.redirect(url)
                return
            raise HTTPError(403)

        group = yield get_group_by_user(current_user)
        if group != (1 or 2):
            raise HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper


def superuser_required(method):  # 超级管理员登录装饰器
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        current_user = self.current_user
        if not self.current_user:
            if self.request.method in ("GET", "HEAD"):
                url = self.get_login_url()
                if "?" not in url:
                    if urlparse.urlsplit(url).scheme:
                        # if login url is absolute, make next absolute too
                        next_url = self.request.full_url()
                    else:
                        next_url = self.request.uri
                    url += "?" + urlencode(dict(next=next_url))
                self.redirect(url)
                return
            raise HTTPError(403)

        group = yield get_group_by_user(current_user)
        if group != 2:
            raise HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper