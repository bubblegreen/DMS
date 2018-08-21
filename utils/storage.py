#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Xu Hang on 2018-08-21

import os
import json

current_dir = os.path.split(os.path.realpath(__file__))[0]
storage_file_path = current_dir + '/storage.json'


def get_image_storage():
    return get_storage('images')


def get_container_storage():
    return get_storage('containers')


def update_image_storage(content: dict):
    update_storage('images', content)


def update_container_storage(content: dict):
    update_storage('containers', content)


def get_storage(key):
    with open(storage_file_path, encoding='utf8') as f:
        storage_dict = json.load(f)
    return storage_dict[key]


def update_storage(key, content):
    with open(storage_file_path, encoding='utf8', mode='w+') as f:
        storage_dict = json.load(f)
        storage_dict[key] = content
        f.write(json.dumps(storage_dict))


if __name__ == '__main__':
    get_image_storage()
    pass
