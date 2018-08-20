var Image = function () {
};

function startLoad(id){
    var identify = '#' + id;
    $(identify).modal({backdrop:'static',keyboard:false});
}
function stopLoad(id){
    var identify = '#' + id;
    $(identify).modal('hide');
}

Image.getList = function () {
    var element = $("#imageList");
    //element.empty();
    element.load('/image/list', function () {
        stopLoad('loadDiv');
    });
};

Image.remove = function (name, tag) {
    //event.preventDefault();
    $.ajax({
        type: 'post',
        url: '/image/remove',
        data: JSON.stringify({"name": name, "tag": tag, "local": false, "remote": true}),
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        dataType: 'json',
        beforeSend: function(){
            startLoad('loadDiv');
        },
        success: function (data) {
            if ('state' in data && data.state === 'error') {
                alert(data.message);
            }
            else {
                Image.getList();
            }
        }
    })
};

Image.pull = function (name, tag) {
    event.preventDefault();
    $.ajax({
        type: 'post',
        url: '/image/pull',
        data: JSON.stringify({"name": name, "tag": tag, "local": true, "remote": false}),
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        dataType: 'json',
        beforeSend: function(){
            startLoad('loadDiv');
        },
        success: function (data) {
            if ('state' in data && data.state === 'error') {
                alert(data.message);
            }
            else {
                Image.getList();
            }
        }
    })
};