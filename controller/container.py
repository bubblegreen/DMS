#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Xu Hang on 2018-08-16

from vo.container import Container
import json
from service import container
from flask import request, blueprints, render_template
# from utils import storage as sg

container_view = blueprints.Blueprint('container', __name__)


@container_view.route('/container/list')
def get_container_list():
    res = container.get_all_container()
    return json.dumps(res)


@container_view.route('/container/filter')
def get_container_filtered():
    image = request.args.get('image')
    ancestor = [image, ]
    res = container.get_filtered_container(ancestor=ancestor)
    return render_template('container_list.html', image=image, containers=list(res['containers']))


@container_view.route('/container/start')
def start_container():
    container_name = request.args.get('name')
    res = container.start_container(container_name)
    return json.dumps(res)


@container_view.route('/container/stop')
def stop_container():
    container_name = request.args.get('name')
    res = container.stop_container(container_name)
    return json.dumps(res)


@container_view.route('/container/restart')
def restart_container():
    container_name = request.args.get('name')
    res = container.restart_container(container_name)
    return json.dumps(res)


@container_view.route('/container/remove')
def remove_container():
    container_name = request.args.get('name')
    res = container.remove_container(container_name)
    return json.dumps(res)


@container_view.route('/container/create', methods=['POST'])
def create_container():
    param_dict = json.loads(request.data.decode())
    exp_port_dict = {}
    for expPort in param_dict['expPort']:
        exp_port_dict[expPort] = {}
    env_lst = []
    for env in param_dict['env']:
        env_lst.append(env)
    volume_lst = []
    for volume in param_dict['volume']:
        volume_lst.append(volume)
    bind_ip_dict = {}
    for exp_ip, host_port in zip(param_dict['expPort'], param_dict['hostPort']):
        bind_ip_dict[exp_ip] = [{'HostPort': host_port}]
    container_vo = Container(param_dict['name'], param_dict['image'], exp_port_dict, env_lst, volume_lst, bind_ip_dict)
    res = container.create_container(container_vo)
    # container_storage = sg.get_container_storage()
    # container_storage[param_dict['name']] = param_dict['desp']
    # sg.update_container_storage(container_storage)
    return json.dumps(res)


@container_view.route('/container/new')
def container_new():
    image = request.args.get('image')
    return render_template('container_new.html', image=image)


if __name__ == '__main__':
    pass
