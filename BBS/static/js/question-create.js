let editor = new Simditor({
    textarea: $('#question-content'),
    placeholder: '请输入18-10000字的详细描述...',
    oolbarFloat: true,
    toolbarFloatOffset: 0,
    cleanPaste: true,
    pasteImage: true,//允许粘贴图片
    toolbarHidden: false,
    locale: 'zh-CN',
    toolbar: [
        'title',
        'bold',
        'italic',
        'underline',
        'strikethrough',
        'fontScale',
        'color',
        'ol',
        'ul',
        'code',
        'image',
        'blockquote',
        'table',
        'link',
        'hr',
        'indent',
        'outdent',
        'alignment'],
    upload : {
            url : '/question/picload', //文件上传的接口地址
            params: null, //键值对,指定文件上传接口的额外参数,上传的时候随文件一起提交
            fileKey: 'pic', //服务器端获取文件数据的参数名
            connectionCount: 3,
            leaveConfirm: '正在上传文件...'
        }
});

$('#submit-question').click(function () {
    let abstract = $('#question-abstract').val();
    let content = $('#question-content').val();
    let tag_id = $('#question-tag').find('option:selected').attr('id');
    if(!abstract.match('^[\\s\\S]{7,40}$')) {
        $('#question-abstract').css('border', '1px solid red');
        $('#editorForm').prepend("<div id='absMessage' class='alert alert-danger'>简述长度不符合要求</div>");
        setTimeout(function () {
           $('#absMessage').remove();
        }, 1000);
        return false;
    }else {
        $('#absMessage').remove();
        $('#question-abstract').css('border', '');
    }
    if(!content.match('^[\\s\\S]{18,10240}$')){
        $('#textareaForm').css('border', '1px solid red');
        $('#editorForm').prepend("<div id='absMessage' class='alert alert-danger'>问题描述不符合长度</div>");
        setTimeout(function () {
            $('#absMessage').remove();
        }, 1000);
        return false;
    }else {
        $('#question-content').css('border', '');
    }
    $.ajax({
        url: '/question/create',
        type: 'post',
        data: {
            abstract: abstract,
            content: content,
            tag_id: tag_id
        },
        dataType: 'json',
        success: function (res) {
            if(res.status === 200 && res.data) {
                window.location.href = '/question/detail/' + res.data.qid + encodeURI('?m=创建成功&e=success');
            }else if(res.status === 200001 || res.status === 200002) {
                $('#editorForm').prepend("<div id='regMessage' class='alert alert-danger'>"+ res.message +"</div>");
            }
        }
    });
    return false
});