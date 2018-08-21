#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Xu Hang on 2018-08-15


class Image:
    def __init__(self, name, tag, local=None, remote=None, desp=None):
        self.name = name
        self.tag = tag
        self.local = local
        self.remote = remote
        self.desp = desp

    def __str__(self) -> str:
        return "{'name':'%s', 'tag':'%s','local':'%s','remote':'%s', 'desp': '%s'}" \
               % (self.name, self.tag, self.local, self.remote, self.desp)

    def __repr__(self) -> str:
        return "{'name':'%s', 'tag':'%s','local':'%s','remote':'%s', 'desp': '%s'}" \
               % (self.name, self.tag, self.local, self.remote, self.desp)

    def __eq__(self, o: object) -> bool:
        if o is None:
            return False
        if not isinstance(o, Image):
            return False
        return self.name == o.name and self.tag == o.tag


if __name__ == '__main__':
    pass
