#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @FileName  :StatusCode.py
# @Time      :2023/1/7 22:21
# @Author    :lovemefan
# @email     :lovemefan@outlook.com

from enum import Enum


class StatusCode(Enum):
    """存储状态的枚举类， 枚举类的值不可相等"""
    # 请求超时
    REQUEST_TIMEOUT = 0
    # 404 not found
    NOT_FOUND = 1
    # token 可用
    TOKEN_AVAILABLE = 2
    # token 不可用
    TOKEN_NOT_AVAILABLE = 3
    # 用户名或密码为空
    USERNAME_OR_PASSWORD_EMPTY = 4
    # 用户名或密码错误
    USERNAME_OR_PASSWORD_ERROR = 5
    # token 超时失效
    TOKEN_TIMEOUT = 6
    # 权限不足
    PERMISSION_DENIED = 7
    # 权限可用
    PERMISSION_AVAILABLE = 8
    # 添加用户成功
    ADD_USER_SUCCESS = 9
    # 添加用户失败
    ADD_USER_FAILED = 10
    # 请求缺少参数
    MISSPARAMETERS = 11

    # 删除用户失败
    DELETE_USER_FAILED = 12
    # 修改用户失败
    MODIFY_USER_FAILED = 13
    # 用户不存在
    USER_NOT_EXIST = 14
    # 采样率错误
    SAMPLE_RATE_ERROR = 15
    # 识别成功
    RECOGNITION_FINISHED = 16