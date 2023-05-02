#!/usr/bin/python3
# -*- coding:utf-8 -*-
# @FileName  :app.py
# @Time      :2023/1/7 17:02
# @Author    :lovemefan
# @email     :lovemefan@outlook.com
import sys
import os
from concurrent import futures
from multiprocessing import Process

import grpc

from backend.config.Config import Config
from backend.runtime.grpc import offlineASR_pb2_grpc
from backend.runtime.grpc.paraformerAsrGrpcService import ParaformerASRServicer
from backend.utils.logger import logger

sys.path.append(os.getcwd())
from sanic import Sanic, Request
from sanic.response import json, HTTPResponse
import os
from sanic_openapi import swagger_blueprint
from backend.route.RecognitionRoute import recognition_route

app = Sanic("paraformer-webserver")


@app.middleware("request")
def cors_middle_req(request: Request):
    """路由需要启用OPTIONS方法"""
    if request.method.lower() == 'options':
        allow_headers = [
            'Authorization',
            'content-type'
        ]
        headers = {
            'Access-Control-Allow-Methods':
                ', '.join(request.app.router.get_supported_methods(request.path)),
            'Access-Control-Max-Age': '86400',
            'Access-Control-Allow-Headers': ', '.join(allow_headers),
        }
        return HTTPResponse('', headers=headers)


@app.middleware("response")
def cors_middle_res(request: Request, response: HTTPResponse):
    """跨域处理"""
    allow_origin = '*'
    response.headers.update(
        {
            'Access-Control-Allow-Origin': allow_origin,
        }
    )


def start_grpc_server(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    offlineASR_pb2_grpc.add_ASRServicer_to_server(ParaformerASRServicer(), server)
    port = "[::]:" + str(port)
    server.add_insecure_port(port)
    server.start()
    logger.info("grpc server started!")
    server.wait_for_termination()


app.blueprint(swagger_blueprint)
app.blueprint(recognition_route)

if __name__ == '__main__':
    http_port = int(Config.get_instance().get("http.port"))
    grpc_port = int(Config.get_instance().get("grpc.port"))
    # if env $port is none ,get the config port or default port
    http_port = os.environ.get('PORT', http_port)
    grpc_server = Process(target=start_grpc_server, args=(grpc_port,))
    grpc_server.start()
    app.run(host="0.0.0.0", port=http_port)
