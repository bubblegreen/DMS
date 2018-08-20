var Container = function () {

};

url_obj = {
    stop: "/container/stop?name=",
    start: "/container/start?name=",
    restart: "/container/restart?name=",
    remove: "/container/remove?name=",
    create: "/container/create",
    createNew: '/container/new?image='
};

Container.getList = function (image) {
    var modalDiv = $('#containerModal');
    var modalBody = $('#containerList');
    var url = '/container/filter?image=' + image;
    startLoad('loadDiv');
    modalBody.load(url, function () {
        stopLoad('loadDiv');
        modalDiv.modal({backdrop: 'static'});
    })
};

var containerAction = function (action, name, image) {
    var url = url_obj[action] + name;
    $.ajax({
        type: 'get',
        url: url,
        headers: {
            'Accept': 'application/json'
        },
        beforeSend: function () {
            startLoad('loadSubDiv');
        },
        success: function (data) {
            data = JSON.parse(data);
            if ('state' in data && data.state === 'error') {
                stopLoad('loadSubDiv');
                alert(data.message);
            }
            else {
                var modalBody = $('#containerList');
                var url = '/container/filter?image=' + image;
                modalBody.load(url, function () {
                    stopLoad('loadSubDiv');
                })
            }
        }
    })
};

Container.stop = function (name, image) {
    containerAction('stop', name, image);
};

Container.start = function (name, image) {
    containerAction('start', name, image);
};

Container.restart = function (name, image) {
    containerAction('restart', name, image);
};

Container.remove = function (name, image) {
    containerAction('remove', name, image);
};

Container.createNew = function(image, tag){
    var modalDiv = $('#containerModal');
    var modalBody = $('#containerList');
    var url = url_obj.createNew + image + ':' + tag;
    modalBody.load(url, function () {
        modalDiv.modal({backdrop: 'static'});
    })
}

Container.create = function(image){
    var name = $('#name').val();
    var exportPortLst = $('#expPort').val().split(',');
    var hostPortLst = $('#hostPort').val().split(',');
    var volumeLst = $('#volume').val().split(',');
    var envLst = $('#env').val().split(',');
    $.ajax({
        type: 'post',
        url: url_obj.create,
        data: JSON.stringify({"name": name, "image": image, "expPort": exportPortLst, "volume": volumeLst, "env": envLst, 'hostPort': hostPortLst}),
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        dataType: 'json',
        beforeSend: function(){
            startLoad('loadSubDiv');
        },
        success: function (data) {
            stopLoad('loadSubDiv');
            if ('state' in data && data.state === 'error') {
                alert(data.message);
            }
            else {
                alert('success');
            }
         }
    })
}
