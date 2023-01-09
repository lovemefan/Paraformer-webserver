#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @FileName  :SpeechException.py
# @Time      :2023/1/7 22:19
# @Author    :lovemefan
# @email     :lovemefan@outlook.com
import sanic

from sanic.exceptions import SanicException


class MissParameters(SanicException):
    def __init__(self, massage="miss parameters"):
        super().__init__(massage)


class SpeechSampleRateException(SanicException):
    def __init__(self, massage="sample rate is invalid"):
        super().__init__(massage)
