# -*- coding:utf-8 -*-
# @FileName  :str2bool.py
# @Time      :2023/3/30 19:13
# @Author    :lovemefan
# @Email     :lovemefan@outlook.com

def str2bool(bool_str: str):
    if bool_str.lower() in ['true', 'yes']:
        return True
    elif bool_str.lower() in ['false', 'no']:
        return False
    else:
        raise ValueError(f"Do not support {bool_str}")