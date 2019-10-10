$('#search-user').keydown(function (event) {
    if(event.keyCode === 13) {
        let s = $('#search-user').val();
        if(!s.match('\\w{2,12}')) {
            $('#search-user').val('');
            $('#search-user').css('border', '1px solid red');
            $('#search-user').attr('placeholder', '用户名应该为2-12位之间的字母数字下划线');
            return false;
        }else {
            $('#search-user').val('');
            $('#search-user').css('border', '');
            $('#search-user').attr('placeholder', '查询用户');
        }
        $.ajax({
            url: '/user/search?s=' + s,
            type: 'get',
            dataType: 'json',
            data: {},
            success: function (res) {
                if(res.status === 200 && res.data) {
                    let userList = res.data.user_list;
                    let strHTML = "";
                    for (let i in userList) {
                        strHTML += "<div class=\"list-group-item list-group-item-success\">\n" +
                            "                <b style=\"color: red\">" + userList[i].rank + " </b>\n" +
                            "                <b style=\"margin-left: 20px;font-size: 20px\">"+ userList[i].username +"</b>\n" +
                            "                <b style=\"float: right\"> <span style=\"color: red\">"+ userList[i].point +"</span> 金</b>\n" +
                            "            </div>";
                    }
                    $('#user-list').html(strHTML)
                }else {
                    alert(res.message);
                }
            }
        })
    }
});