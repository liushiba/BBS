let lastQid;
$(document).ready(function () {
    loadQuestion(0);
});

$('#nextQuestions').click(function () {
    loadQuestion(0, lastQid);
});

$('#preQuestions').click(function () {
    loadQuestion(1, lastQid);
});

$('#search-btn').click(function () {
    searchQuestion('#search');
});

$('#result-search-btn').click(function () {
    searchQuestion('#result-search');
});

$('#newest').click(function () {
    loadQuestionByFilter('newest');
});
$('#hotest').click(function () {
    loadQuestionByFilter('hotest');
});
$('#under').click(function () {
    loadQuestionByFilter('under');
});
$('#hasdone').click(function () {
    loadQuestionByFilter('hasdone');
});
$('#prefer').click(function () {
    loadQuestionByFilter('prefer');
});

$('#refreshQ').click(function () {
    loadQuestion();
    $('#preQuestions').removeAttr('disabled');
    $('#nextQuestions').removeAttr('disabled');
});

function filterTag(obj) {
    loadQuestionByFilter(obj.id);
    return false;
}

function loadQuestionByFilter(name) {
    $.ajax({
        url: '/question/filter/' + name,
        type: 'get',
        data: {},
        dataType: 'json',
        success: function (res) {
            if(res.status === 200 && res.data) {
                let data = res.data.question_list;
                let h = "";
                for (let i in data) {
                    h += "<a style='text-align: left' class='list-group-item' href='/question/detail/" + data[i].qid + "'>" +
                        "<span>" + data[i].abstract + "</span>" +
                        "<span style='float: right;margin-right: 25px' class='glyphicon glyphicon-pencil'> " + data[i].answer_count + "</span>" +
                        "<span style='float: right;margin-right: 25px' class='glyphicon glyphicon-eye-open'> " + data[i].view_count + "</span>" +
                        "<span style='float: right;margin-right: 25px' class='glyphicon glyphicon-user'> " + data[i].username + "</span>" +
                        "</a>"
                }
                $('#question-list').html(h);
                $('#preQuestions').attr('disabled', 'disabled');
                $('#nextQuestions').attr('disabled', 'disabled');
            }
        }
    });
}

function searchQuestion(input) {
    let search = $(input).val();
   if(!search.match('^[\\s\\S]{4,14}')) {
       $(input).css('border', '1px solid red')
       $(input).val('');
       $(input).attr('placeholder', '关键字不能少于4个字符大于14个字符');
       return false;
   }else {
       $(input).css('border', '');
   }
   window.location.href = '/question/search?s=' + search;
}

function loadQuestion(pre, last_qid) {
    $.ajax({
        url: '/question/list',
        type: 'get',
        data: {
            pre: pre,
            lqid: last_qid
        },
        dataType: 'json',
        success: function (res) {
            if (res.status === 200 && res.data) {
                let data = res.data.question_list;
                if(data.length) {
                    let h = "";
                    for (let i in data) {
                        h += "<a style='text-align: left' class='list-group-item' href='/question/detail/" + data[i].qid + "'>" +
                            "<span>" + data[i].abstract + "</span>" +
                            "<span style='float: right;margin-right: 25px' class='glyphicon glyphicon-pencil'> " + data[i].answer_count + "</span>" +
                            "<span style='float: right;margin-right: 25px' class='glyphicon glyphicon-eye-open'> " + data[i].view_count + "</span>" +
                            "<span style='float: right;margin-right: 25px' class='glyphicon glyphicon-user'> " + data[i].username + "</span>" +
                            "</a>"
                    }
                    $('#question-list').html(h);
                    lastQid = res.data.last_qid;
                }else {
                    $('#question-list').prepend("<div id='pageMessage' class='alert alert-danger'>没有更多了</div>");
                    setTimeout(function () {
                        $('#question-list').find('#pageMessage').remove();
                    }, 1000);
                }
            }
        }
    })
}