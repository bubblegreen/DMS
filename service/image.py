#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Xu Hang on 2018-08-15

from vo.image import Image
import api.docker_api as d_api
import api.regitstry_api as r_api
from utils import request as rq


def get_images_in_registry():
    repo_prefix = rq.registry_host.replace('http://', '') + '/'
    repositories_in_registry = rq.request_registry(r_api.get_repositeries).json().get('repositories')
    images_in_registry = []
    for repo in repositories_in_registry:
        tags = rq.request_registry(r_api.get_image_tags, path_params=repo).json().get('tags')
        for tag in tags:
            image = Image(repo_prefix + repo, tag, False, True)
            images_in_registry.append(image)
    return images_in_registry


def get_images_in_docker():
    images_in_docker = []
    repositories = rq.request_docker(d_api.list_image).json()
    for repo in repositories:
        repo_tags = repo.get('RepoTags')
        for repo_tag in repo_tags:
            name, tag = repo_tag.rsplit(':', maxsplit=1)
            image = Image(name, tag, True, False)
            images_in_docker.append(image)
    return images_in_docker


def get_all_images() -> list:
    image_list = []
    images_in_registry = get_images_in_registry()
    images_in_docker = get_images_in_docker()
    for image in images_in_registry:
        image_merged = image
        image_merged.local = True if image in images_in_docker else False
        image_list.append(image_merged)
    return image_list


def pull_image(image: Image) -> dict:
    query_param = 'fromImage=%s:%s' % (image.name, image.tag)
    response = rq.request_docker(d_api.pull_image, query_params=query_param)
    if response.status_code == 200:
        return {'state': 'ok', 'message': ''}
    return {'state': 'error', 'message': response.text}


def remove_image_local(image: Image) -> dict:
    path_param = image.name
    response = rq.request_docker(d_api.remove_image, path_params=path_param)
    if response.status_code == 200:
        return {'state': 'ok', 'message': ''}
    return {'state': 'error', 'message': response.text}


if __name__ == '__main__':
    im = Image('192.168.23.26:5000/mariadb', 'latest')
    r = remove_image_local(im)
    print(r)
