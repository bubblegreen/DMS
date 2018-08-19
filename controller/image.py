#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Xu Hang on 2018-08-16

from service import image
from flask import request, render_template, blueprints
import json
from vo.image import Image
import logging


image_view = blueprints.Blueprint('image', __name__)


@image_view.route('/image/list')
def get_image_list():
    logging.debug('request image list')
    images = image.get_all_images()
    return render_template('image_list.html', images=images)


@image_view.route('/image/pull', methods=['POST'])
def pull_image():
    image_dict = json.loads(request.data.decode())
    image_vo = Image("name", "tag")
    image_vo.__dict__ = image_dict
    res = image.pull_image(image_vo)
    return json.dumps(res)


@image_view.route('/image/remove', methods=['POST'])
def remove_image():
    image_dict = json.loads(request.data.decode())
    image_vo = Image("name", "tag")
    image_vo.__dict__ = image_dict
    res = image.remove_image_local(image_vo)
    return json.dumps(res)


if __name__ == '__main__':
    pass
