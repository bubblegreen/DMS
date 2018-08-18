var Image = function () {
};

Image.getList = function () {
    var element = $("#content");
    element.empty();
    element.load('/image/list', function () {
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