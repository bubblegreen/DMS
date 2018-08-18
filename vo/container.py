#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Xu Hang on 2018-08-16

import json


class Container:
    def __init__(self, name, image, port_exp={}, env=[], bind=[], port_bind={}):
        self.name = name
        self.Image = image
        self.ExposedPorts = port_exp
        self.Env = env
        self.HostConfig = {}
        self.HostConfig['Binds'] = bind
        self.HostConfig['PortBindings'] = port_bind


class ContainerEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, set):
            return str(o)
        if isinstance(o, Container):
            json_dick = {"Image": o.Image, "ExposedPorts": o.ExposedPorts,
                        "Env": o.Env, "HostConfig": o.HostConfig}
            return json_dick
        return json.JSONEncoder.default(self, o)


if __name__ == '__main__':
    pass
