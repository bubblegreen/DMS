let Container = function () {
};

Container.action = function (action) {
    let url = '/container/action/' + action;
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
    let btnGroup = $('.btn-group');
    btnGroup.children().attr('disabled', true);
    $.ajax({
        url: url,
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
                    btnGroup.children().attr('disabled', false);
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
                    btnGroup.children().attr('disabled', false);
                }
            }, false);
        }
    });
};
