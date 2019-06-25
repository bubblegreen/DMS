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
    // todo
};
