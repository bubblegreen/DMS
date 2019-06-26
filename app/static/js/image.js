let image = function () {
};

image.pull = function (event) {
    event.preventDefault();
    let btn = $('#pull');
    btn.button('loading');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        }
    });
    $.ajax({
        url: '/image/pull',
        type: 'post',
        data: $('form').serialize(),
        dataType: 'json',
        processData: false,
        success: function (result) {
            let msg = $('#msg');
            if ('html' in result) {
                let form = $('form');
                form.empty();
                form.append($(result.html));
            } else {
                let message = result.msg;
                if (message.indexOf('success') > 0) {
                    msg.css('color', 'green');
                    $('#table').dataTable().api().ajax.reload();
                } else {
                    msg.css('color', 'red');
                }
                msg.text(message);
                msg.show();
                setTimeout(function () {
                    msg.hide();
                }, 3000);
            }
            btn.button('reset');
        }
    });
};

image.remove = function () {
    let ids = [];
    let selected = $('input:checked');
    for (let i = 0; i < selected.length; i++) {
        ids.push(selected[i].value);
    }
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        }
    });
    let removeBtn = $('#remove');
    removeBtn.attr('disabled', true);
    $.ajax({
        url: '/image/remove',
        type: 'post',
        data: JSON.stringify(ids),
        contentType: 'application/json',
        dataType: 'json',
        success: function (failList) {
            $('#table').dataTable().api().ajax.reload(function () {
                for (let index in failList) {
                    let hashId = failList[index];
                    $('input[value="' + hashId + '"]').prop('checked', true);
                }
                if ($('input:checked').length > 0) {
                    removeBtn.attr('disabled', false);
                }
            }, false);
        },
        error: function () {
            $('#table').dataTable().api().ajax.reload(function () {
                for (let index in ids) {
                    let hashId = ids[index];
                    let row = $('input[value="' + hashId + '"]');
                    if (row) {
                        row.prop('checked', true);
                    }
                }
                if ($('input:checked').length > 0) {
                    removeBtn.attr('disabled', false);
                }
            }, false);
        }
    });
};

image.show_detail_view = function (image_hash) {
    let url = '/image/detail/' + image_hash;
    let container = $("#main-content");
    container.empty();
    container.load(url);
};

image.refreshTagList = function () {
    let url = '/image/tag_list/' + id;
    let tag_list = $('#tag-list');
    tag_list.empty();
    tag_list.load(url);
};

image.tag = function (event) {
    event.preventDefault();
    let btn = $('#tagImage');
    btn.button('loading');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        }
    });
    $.ajax({
        url: '/image/tag/' + id,
        type: 'post',
        data: $('form').serialize(),
        dataType: 'json',
        processData: false,
        success: function (result) {
            let msg = $('#msg');
            if ('ok' === result) {
                image.refreshTagList();
                $('#name').val('');
            } else {
                let message = result.msg;
                msg.text(message);
                msg.show();
                setTimeout(function () {
                    msg.hide();
                }, 3000);
            }
            btn.button('reset');
        },
        error: function (data) {
            console.log(data);
            btn.button('reset');
        }
    });
};

image.untag = function (event) {
    event.preventDefault();
    let btn = $(event.target);
    let tag = btn.parent().prev().text();
    let url = '/image/untag';
    btn.button('loading');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        }
    });
    $.ajax({
        url: url,
        type: 'post',
        data: JSON.stringify({"tag": tag}),
        contentType: "application/json",
        processData: false,
        success: function (result) {
            if (result === 'ok') {
                image.refreshTagList();
            }
            btn.button('reset');
        },
        error: function (data) {
            console.log(data);
            btn.button('reset');
        }
    });
};
