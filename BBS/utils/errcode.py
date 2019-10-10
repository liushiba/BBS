"""
错误码: 用来记录JSON响应的错误码
"""
# AUTH
LOGIN_VCODE_ERR = (100001, '验证码错误或超时')
USERNAME_ERR = (100002, '用户名错误')
PASSWORD_ERR = (100003, '密码错误')
USER_EXISTS = (100004, '用户名已存在')
USER_CREATE_ERR = (100005, '用户创建失败')
USER_HAS_NOT_VALIDATE = (100006, '用户未登录')

# QUESTION/ANSWER
PARAMETER_ERR = (200001, '参数错误')
CREATE_ERR = (200002, '创建失败')
PARAMETER_TOO_SHORT = (200003, '参数太短')
DEL_ERR = (200004, '删除失败')
ADD_POINT_ERR = (200005, '加分失败，请联系管理员')
ADOPT_COUNT_ERR = (200006, '最多只能采纳三个答案')