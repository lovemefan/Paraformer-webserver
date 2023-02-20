#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @FileName  :RecognitionRoute.py
# @Time      :2023/1/7 22:18
# @Author    :lovemefan
# @email     :lovemefan@outlook.com

from sanic import Blueprint
from sanic.response import json

from backend.exception.SpeechException import SpeechSampleRateException, MissParameters
from backend.model.ResponseBody import ResponseBody
from backend.service.ParaformerAsrService import ParaformerAsrService

recognition_route = Blueprint('speech', url_prefix='/api/speech', version=1)
recongnitionService = ParaformerAsrService()



@recognition_route.exception(SpeechSampleRateException)
async def speech_sample_rate_exception(request, exception):
    response = ResponseBody(
        message=str(exception),
        code=500
    )
    return json(response.__dict__, 408)


@recognition_route.post('/recognition')
async def recognition(request):
    audio_file = request.files.get('audio', None)

    if not audio_file:
        raise MissParameters('audio is empty')

    result = await recongnitionService.transcribe(audio_file)
    return json(
        ResponseBody(message=f'Success',
                     data=result).__dict__,
        200)
