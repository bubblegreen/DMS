#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Xu Hang on 2018-08-15

import api.docker_api as d_api
from utils import request as rq
import json
from vo.container import Container, ContainerEncoder
from utils import storage as sg


def create_container(container_vo: Container) -> dict:
    query_param = 'name=%s' % container_vo.name
    # del container.name
    request_body = json.dumps(container_vo, cls=ContainerEncoder)
    header = {'Content-Type': 'application/json'}
    response = rq.request_docker(d_api.create_container, data=request_body, query_params=query_param, header=header)
    if response.status_code == 201:
        return response.json()
    return {'state': 'error', 'message': response.text}


def get_all_container() -> dict:
    return get_filtered_container()


def get_filtered_container(all_container=True, ancestor: list = None, name: list = None, status: list = None) -> dict:
    filter_param_dict = {}
    if ancestor:
        filter_param_dict['ancestor'] = ancestor
    if name:
        filter_param_dict['name'] = name
    if status:
        filter_param_dict['status'] = status
    filter_param = json.dumps(filter_param_dict)
    query_param = 'all=%s&filters=%s' % (all_container, filter_param)
    response = rq.request_docker(d_api.list_container, query_params=query_param)
    if response.status_code == 200:
        container_storage = sg.get_container_storage()
        container_list = response.json()
        containers = []
        for container in container_list:
            container_name = (container['Names'][0])[1:]
            container_status = container['Status']
            # container_desp = container_storage[container_name]
            # containers.append({"name": container_name, "status": container_status, "desp": container_desp})
            containers.append({"name": container_name, "status": container_status})
        return {"containers": containers}
    return {'state': 'error', 'message': response.text}


def remove_container(container_name, v=False, force=False, link=False) -> dict:
    path_param = container_name
    query_param = 'v=%s&force=%s&link=%s' % (v, force, link)
    response = rq.request_docker(d_api.remove_container, path_params=path_param, query_params=query_param)
    if response.status_code == 204:
        return {'state': 'ok', 'message': ''}
    return {'state': 'error', 'message': response.text}


def stop_container(container_name) -> dict:
    path_param = container_name
    response = rq.request_docker(d_api.stop_container, path_params=path_param)
    if response.status_code == 204:
        return {'state': 'ok', 'message': ''}
    return {'state': 'error', 'message': response.text}


def start_container(container_name) -> dict:
    path_param = container_name
    response = rq.request_docker(d_api.start_container, path_params=path_param)
    if response.status_code == 204:
        return {'state': 'ok', 'message': ''}
    return {'state': 'error', 'message': response.text}


def restart_container(container_name) -> dict:
    path_param = container_name
    response = rq.request_docker(d_api.restart_container, path_params=path_param)
    if response.status_code == 204:
        return {'state': 'ok', 'message': ''}
    return {'state': 'error', 'message': response.text}


if __name__ == '__main__':
    # container = Container('mariadb', '192.168.23.26:5000/mariadb:latest', {'3306/tcp': {}},
    #                       ['MYSQL_ROOT_PASSWORD=aisino'], ['/home/mariadb:/var/lib/mysql'],
    #                       {"3306/tcp": [{"HostPort": "3308"}]})
    # r = create_container(container)
    # r = start_container(container.name)

    r = get_filtered_container(ancestor=['192.168.23.26:5000/mariadb:latest', ])
    print(r)
