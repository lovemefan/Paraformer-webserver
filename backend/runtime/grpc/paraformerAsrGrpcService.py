# -*- coding:utf-8 -*-
# @FileName  :paraformerAsrGrpcService.py
# @Time      :2023/3/30 16:44
# @Author    :lovemefan
# @Email     :lovemefan@outlook.com
import asyncio
from concurrent import futures
import grpc
import json
import time

from backend.runtime.grpc import offlineASR_pb2_grpc
from backend.runtime.grpc.offlineASR_pb2 import Response
from backend.service.ParaformerAsrOfflineService import ParaformerAsrService
from backend.utils.AudioHelper import AudioReader
from backend.utils.logger import logger


class ParaformerASRServicer(offlineASR_pb2_grpc.ASRServicer):
    def __init__(self):
        logger.info("Paraformer ASRServicer init")
        self.init_flag = 0
        self.client_buffers = {}
        self.client_transcription = {}
        self.inference_16k_pipeline = ParaformerAsrService()

    def Recognize(self, request, context):
        data = request.audio_data
        array = AudioReader.read_pcm_byte(data)
        begin_time = int(round(time.time() * 1000))
        asr_result = self.inference_16k_pipeline.infer_without_async(array)
        asyncio.sleep(0)
        end_time = int(round(time.time() * 1000))
        delay_str = str(end_time - begin_time)
        logger.debug("user: %s , delay(ms): %s, text: %s " % (request.user, delay_str, asr_result))
        result = {}
        result["success"] = True
        result["server_delay_ms"] = delay_str
        result["text"] = asr_result
        return Response(sentence=json.dumps(result, ensure_ascii=False), user=request.user,
                       language=request.language)


