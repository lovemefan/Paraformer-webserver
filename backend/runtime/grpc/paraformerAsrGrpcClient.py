# -*- coding:utf-8 -*-
# @FileName  :paraformerAsrGrpcClient.py
# @Time      :2023/3/30 18:05
# @Author    :lovemefan
# @Email     :lovemefan@outlook.com

import grpc
import asyncio


from backend.runtime.grpc import offlineASR_pb2
from backend.runtime.grpc.offlineASR_pb2_grpc import ASRStub
from backend.utils.AudioHelper import AudioReader


def transcribe_audio_bytes(stub, chunk, user='test', language='zh-CN'):
    req = offlineASR_pb2.Request()
    if chunk is not None:
        req.audio_data = chunk
    req.user = user
    req.language = language
    return stub.Recognize(req)


async def record(host, port, chunk, asr_user, language):
    with grpc.insecure_channel('{}:{}'.format(host, port)) as channel:
        stub = ASRStub(channel)
        response = transcribe_audio_bytes(stub, chunk, user=asr_user, language=language)
        print(response)


if __name__ == '__main__':

    print("* recording")
    with open('/dataset/speech/aishell/data_aishell/wav/test/S0764/BAC009S0764W0495.wav', 'rb') as wav:
        data = wav.read()

    asyncio.run(record('222.197.219.18', '18889', data, 'test', 'zh-CN'))

    print("recording stop")


