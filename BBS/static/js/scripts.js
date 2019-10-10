$(document).ready(function() {
    $.backstretch("/static/img/backgrounds/background.jpg");
    $('.registration-form fieldset:first-child').fadeIn('slow');
    if($('#baseMessage')) {
        setTimeout(function () {
            $('#baseMessage').remove();
            }, 1000);
    }
    refreshCurrentStatus();
    requestAnswerStatus();
});
$('#signBtn').click(function () {
   if($(this).html() !== '登录') {
       $('#signOutModal').modal('show');
       $('#signOut').click(function () {
           window.location.href = '/auth/logout?next=' + getCurrentUrl();
       });
       return false;
   }else{
       window.location.href = '/auth/login?next=' + getCurrentUrl();
       return false;
   }
});

$('#signBtn #status').click(function () {
    window.location.href = '/answer/unread';
    return false;
});

function getCurrentUrl() {
    return window.location.pathname;
}

function getQueryString(name) {
    let reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
    let r = window.location.search.substr(1).match(reg);
    if (r != null) return unescape(r[2]); return null;
}

function refreshCurrentStatus() {
    $.ajax({
        url: '/answer/status/current',
        type: 'get',
        data: {},
        dataType: 'json',
        success: function (res) {
            if(res.status === 200 && res.data) {
                $('#signBtn #status').html(res.data.answer_count);
            }
        }
    })
}

function getCookie(name) {
    let arr,reg=new RegExp("(^| )"+name+"=([^;]*)(;|$)");
    if(arr=document.cookie.match(reg))
        return unescape(arr[2]);
    else {
        return null;
    }
}

function requestAnswerStatus() {
    jQuery.getJSON('/answer/status',
        function (res) {
        $('#signBtn #status').html(res.answer_count);
        requestAnswerStatus()
    })
}
