#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Xu Hang on 2018-08-15

import requests
from configparser import ConfigParser
import os


current_dir = os.path.split(os.path.realpath(__file__))[0]
cfg_file_path = current_dir + '/../config.cfg'
config = ConfigParser()
config.read(cfg_file_path)
registry_host = config.get('registry', 'url')
docker_host = config.get('docker', 'url')


def request_registry(api, data=None, path_params=None, query_params=None, header=None):
    host = registry_host
    return request(host, api, data, path_params, query_params, header)


def request_docker(api, data=None, path_params=None, query_params=None, header=None):
    host = docker_host
    return request(host, api, data, path_params, query_params, header)


def request(host, api, data=None, path_params=None, query_params=None, header=None):
    url = host + api['path']
    url = url if path_params is None else url % path_params
    url = url if query_params is None else '%s?%s' % (url, query_params)
    response = None
    if api['type'] == 'get':
        response = requests.get(url, headers=header)
    elif api['type'] == 'post':
        response = requests.post(url, data, headers=header)
    elif api['type'] == 'delete':
        response = requests.delete(url, headers=header)
    return response


if __name__ == '__main__':
    pass
