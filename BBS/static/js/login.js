let loginSign;

$(document).ready(function () {
   refreshLoginVcode();
});

$('#loginVcode').click(function () {
    refreshLoginVcode();
});

$('#submitSignup').click(function () {
    let username = $('#form-username').val();  // 获取用户名
    let password = $('#form-password').val();  // 获取密码
    let vcode = $('#form-vcode').val();        // 获取验证码
    // 使用正则表达式检测用户名是否在4-12位之间
    if(!username.match('^\\w{4,12}$')) {  // 如果不是
        $('#form-username').css('border', 'solid red'); // 更改边框样式
        $('#form-username').val('');    // 设置用户名为空
        $('#form-username').attr('placeholder', '用户名长度应该在4-12位之间'); // 显示提示信息
        return false;
    }else { // 如果是
        $('#form-username').css('border', '');  // 设置用户名边框样式为空白
    }
    // 使用正则表达式检测密码是否在6-20位之间
    if(!password.match('^\\w{6,20}$')) {
        $('#form-password').css('border', 'solid red');
        $('#form-password').val('');
        $('#form-password').attr('placeholder', '密码长度应该在6-20位之间');
        return false;
    }else {
        $('#form-password').css('border', '');
    }
    // 使用正则表达式检测验证码是否为4位
    if(!vcode.match('^\\w{4}$')) {
        $('#form-vcode').css('border', 'solid red');
        $('#form-vcode').val('');
        $('#form-vcode').attr('placeholder', '验证码长度为4位');
        return false;
    }else {
        $('#form-vcode').css('border', '');
    }
    // 使用Ajax 异步方式提交数据
    $.ajax({
        url: '/auth/signup', // 提交的URL
        type: 'post',         // 类型为Post
        data: {                // 设置提交的数据
            username: username, // 用户名
            password: password, // 密码
            vcode: vcode,       // 验证码
            sign: loginSign     // 注册标识
        },
        dataType: 'json',      // 数据类型
        success: function (res) { // 回调函数
            if(res.status === 200 && res.data) {  // 如果返回码是200 并且包含返回数据
                window.location.href = getQueryString('next') || '/' + encodeURI('?m=登录成功&e=success'); // 跳转到首页
            }else if(res.status === 100001) {  // 验证码错误或超时
                $('#form-vcode').css('border', 'solid red');
                $('#form-vcode').val('');
                $('#form-vcode').attr('placeholder', res.message);
            }else if(res.status === 100004) {  // 用户名已存在
                $('#form-username').css('border', 'solid red');
                $('#form-username').val('')
                $('#form-username').attr('placeholder', res.message);
            }else if(res.status === 100005) { // 用户创建失败
                $('.registration-form').prepend("<div id='regMessage' class='alert alert-danger'>注册失败</div>");
                setTimeout(function () {
                    $('.registration-form').find('#regMessage').remove(); // 移除错误信息
                    }, 1500);
            }
        }
    })
});

$('#submitLogin').click(function () {
    let username = $('#form-username').val();
    let password = $('#form-password').val();
    let vcode = $('#form-vcode').val();
    if(!username.match('^\\w{4,12}$')) {
        $('#form-username').css('border', 'solid red');
        $('#form-username').val('');
        $('#form-username').attr('placeholder', '用户名长度应该在4-12位之间');
        return false;
    }else {
        $('#form-username').css('border', '');
    }
    if(!password.match('^\\w{6,20}$')) {
        $('#form-password').css('border', 'solid red');
        $('#form-password').val('');
        $('#form-password').attr('placeholder', '密码长度应该在6-20位之间');
        return false;
    }else {
        $('#form-password').css('border', '');
    }
    if(!vcode.match('^\\w{4}$')) {
        $('#form-vcode').css('border', 'solid red');
        $('#form-vcode').val('');
        $('#form-vcode').attr('placeholder', '验证码长度为4位');
        return false;
    }else {
        $('#form-vcode').css('border', '');
    }
    $.ajax({
        url: '/auth/login',
        type: 'post',
        data: {
            username: username,
            password: password,
            vcode: vcode,
            sign: loginSign,
        },
        dataType: 'json',
        success: function (res) {
            if(res.status === 200 && res.data) {
                window.location.href = getQueryString('next') || '/' + encodeURI('?m=登录成功&e=success');
            }else if(res.status === 100001) {
                $('#form-vcode').css('border', 'solid red');
                $('#form-vcode').val('');
                $('#form-vcode').attr('placeholder', res.message);
            }else if(res.status === 100002) {
                $('#form-username').css('border', 'solid red');
                $('#form-username').val('')
                $('#form-username').attr('placeholder', res.message);
            }else if(res.status === 100003) {
                $('#form-password').css('border', 'solid red');
                $('#form-password').val('');
                $('#form-password').attr('placeholder', res.message);
            }
        }
    })
});

function refreshLoginVcode() {
    $.ajax({
        url: '/auth/v.img',
        type: 'get',
        data: {},
        dataType: 'json',
        success: function (res) {
            if(res.status === 200 && res.data) {
                $('#loginVcode').attr('src', "data:image/png;base64," + res.data.vcode);
                loginSign = res.data.sign;
            }
        }
    })
}