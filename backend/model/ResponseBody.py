#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2020/12/27 下午11:04
# @Author  : lovemefan
# @File    : AsrBody.py
import json


class ResponseBody:
    """The response body of http"""

    def __init__(self, message='Success', code=200, data=""):
        self.message = message
        self.code = code
        self.data = data

    def to_json(self):
        return json.dumps(self.__dict__(), ensure_ascii=False)
