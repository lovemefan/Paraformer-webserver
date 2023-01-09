#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @FileName  :WhisperAsrService.py
# @Time      :2023/1/7 17:01
# @Author    :lovemefan
# @email     :lovemefan@outlook.com
from typing import Union

from backend.decorator.singleton import singleton
import os
import torch
from sanic.request import File
import numpy as np
from backend.utils.logger import logger
from modelscope.pipelines import pipeline

@singleton
class ParaformerAsrService:
    def __init__(self):
        self.model = pipeline('asr-webservice', 'damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch')

    def transcribe(self, audio: Union[np.ndarray, File]):
        result = self.model(audio_in=audio.body)
        return result

