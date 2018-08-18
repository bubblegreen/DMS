#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Xu Hang on 2018-08-15

list_image = {"type": "get", "path": "/images/json"}
remove_image = {"type": "delete", "path": "/images/%s"}
pull_image = {"type": "post", "path": "/images/create"}
list_container = {"type": "get", "path": "/containers/json"}
create_container = {"type": "post", "path": "/containers/create"}
start_container = {"type": "post", "path": "/containers/%s/start"}
stop_container = {"type": "post", "path": "/containers/%s/stop"}
restart_container = {"type": "post", "path": "/containers/%s/restart"}
remove_container = {"type": "delete", "path": "/containers/%s"}

if __name__ == '__main__':
    pass
