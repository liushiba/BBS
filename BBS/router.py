# -*- coding: utf-8 -*-

from tornado.web import StaticFileHandler

from handlers.index_handlers import IndexHandler
from handlers.auth_handlers import LoginHandler, LogoutHandler, SignupHandler, AuthCodeHandler
from handlers.question_handlers import (QuestionListHandler, QuestionCreateHandler, QuestionDeleteHandler,
                                        QuestionUpdateHandler, QuestionDetailHandler, QuestionUploadPicHandler,
                                        QuestionSearchHandler, QuestionFilterHandler)
from handlers.answer_handlers import (AnswerListHandler, AnswerCreateHandler, AnswerDetailHandler, AnswerUpdateHandler,
                                      AnswerDeleteHandler, AnswerStatusHandler, UnreadAnswerHandler, AnswerStatusCurrentHandler,
                                      AnswerAdoptHandler)
from handlers.user_handlers import (UserListHandler, UserSearchHandler)
from handlers.tag_handlers import (TagListHandler,)

from conf import DEFAULT_UPLOAD_PATH

"""
路由文件：
每一块代码代表一个路由配置项，用来对应handlers模块下的每个控制器文件中的类；
"""

# INDEX
ROUTERS = [
    (r'/', IndexHandler), # 首页
    (r'/index', IndexHandler)
]


# USER
ROUTERS += [
    (r'/user/list', UserListHandler),  # 用户列表
    (r'/user/search', UserSearchHandler),  # 用户查询
]


# AUTH
ROUTERS += [
    (r'/auth/login', LoginHandler),  # 登录
    (r'/auth/signup', SignupHandler),  # 注册
    (r'/auth/logout', LogoutHandler),  # 登出
    (r'/auth/v.img', AuthCodeHandler),  # 验证码
]


# QUESTION
ROUTERS += [
    (r'/question/list', QuestionListHandler),  # 问题列表
    (r'/question/create', QuestionCreateHandler),  # 创建问题
    (r'/question/update/(\d+)', QuestionUpdateHandler),  # 更新问题
    (r'/question/detail/(\d+)', QuestionDetailHandler),  # 问题详情
    (r'/question/delete/(\d+)', QuestionDeleteHandler),  # 删除问题
    (r'/question/picload', QuestionUploadPicHandler),  # 上传图片
    (r'/question/search', QuestionSearchHandler),  # 搜索问题
    (r'/question/filter/(\w+)', QuestionFilterHandler),  # 过滤问题
]


# ANSWER
ROUTERS += [
    (r'/answer/list/(\d+)', AnswerListHandler),  # 答案列表
    (r'/answer/create', AnswerCreateHandler),  # 创建答案
    (r'/answer/update/(\d+)', AnswerUpdateHandler),  # 更新答案
    (r'/answer/detail/(\d+)', AnswerDetailHandler),  # 答案详情
    (r'/answer/delete/(\d+)', AnswerDeleteHandler),  # 删除答案
    (r'/answer/status', AnswerStatusHandler),  # 答案状态
    (r'/answer/status/current', AnswerStatusCurrentHandler),  # 当前答案状态
    (r'/answer/unread', UnreadAnswerHandler),  # 未读答案
    (r'/answer/adopt/(\d+)', AnswerAdoptHandler),  # 采纳答案
]


# TAG
ROUTERS += [
    (r'/tag/list', TagListHandler),  # 标签列表
]


# STATICFILES
ROUTERS += [
    (r'/pics/(.*?)$', StaticFileHandler, {'path': DEFAULT_UPLOAD_PATH})  # 静态文件
]