let dm = function () {
};

dm.loadView = function (html) {
    let container = $("#main-content");
    container.empty();
    container.append($(html));
};

dm.showIndexView = function (url) {
    console.log('request view page: ' + url);
    let container = $("#main-content");
    container.empty();
    container.load(url);
};

dm.addMenuClick = function (event) {
    let url = '/' + event.data.viewType;
    dm.showIndexView(url);
};

dm.menu = function (role, mode, endpoint, permissions) {
    $('#endpoint').text(endpoint);
    if (endpoint) {
        $('#docker').show();
    } else {
        $('#docker').hide();
        return;
    }
    if (mode === 'Swarm') {
        if (role !== 'norm') {
            $('li.swarm').show();
        }
        $('li.standalone').hide();
    } else if (mode === 'Standalone') {
        $('li.swarm').hide();
        $('li.standalone').show();
    } else {
        $('li.swarm').hide();
        $('li.standalone').hide();
    }

    // permission
    if (permissions.image) {
        $('#image').show();
    } else {
        $('#image').hide();
    }
    if (permissions.container) {
        $('#container').show();
    } else {
        $('#container').hide();
    }
    if (permissions.volume) {
        $('#volume').show();
    } else {
        $('#volume').hide();
    }
    if (permissions.network) {
        $('#network').show();
    } else {
        $('#network').hide();
    }

    // set setting menus
    if (role !== 'norm') {
        $('#setting').show();
        if (role === 'super') {
            $('li.admin').show();
        } else {
            $('li.admin').hide();
        }
    } else {
        $('#setting').hide();
    }
};

dm.show_edit_view = function (viewName, action, id) {
    let url = id ? ('/' + viewName + '/' + action + '/' + id) : ('/' + viewName + '/' + action);
    let container = $("#main-content");
    container.empty();
    container.load(url);
};

dm.removeEntity = function (entityType) {
    let url = '/' + entityType + '/remove';
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
    $.ajax({
        url: url,
        type: 'post',
        data: JSON.stringify(ids),
        contentType: 'application/json',
        success: function (html) {
            dm.loadView($(html));
        }
    });
};

dm.loadEndpoint = function (event) {
    let endpoint_id = $(event.currentTarget).prev().children('h4').attr('value');
    console.log(endpoint_id);
    $.ajax({
        url: '/load/' + endpoint_id,
        success: function (result) {
            let endpoint_name = result.name;
            let mode = result.mode;
            let endpoint = $('#endpoint');
            endpoint.text(endpoint_name);
            if (endpoint_name) {
                $('#docker').show();
            } else {
                $('#docker').hide();
                return;
            }
            if (mode === 'Swarm') {
                if (result.role !== 'norm') {
                    $('li.swarm').show();
                }
                $('li.standalone').hide();
            } else if (mode === 'Standalone') {
                $('li.swarm').hide();
                $('li.standalone').show();
            } else {
                $('li.swarm').hide();
                $('li.standalone').hide();
            }
            endpoint.parents('a').click();
            dm.showIndexView('/dashboard');
        }
    })
};

dm.textWidth = function ($this) {
    // 获取当前input的value值和字体大小
    var inputVal = $this.val();
    var font = $this.css('font-size');
    //获取容器的宽度
    $(".spanw").text(inputVal).css('font-size', font);
    ;
    var width = $(".spanw").width();
    // 清空容器
    $(".spanw").text('');
    // 设置input宽度
    $this.css('width', width);
};
