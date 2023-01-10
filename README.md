# Paraformer webserver
[中文版README](README-ZH.md)


Paraformer is an efficient non-autoregressive end-to-end speech recognition framework proposed by the speech team of The Academy for Discovery, Adventure, Momentum and Outlook，Alibaba DAMO Academy, with SOTA results on multiple public datasets.
The project is Paraformer Chinese universal speech recognition model, which uses industrial-grade tens of thousands of hours of labeled audio for model training to ensure the universal recognition effect of the model.
The model can be applied to speech input method, voice navigation, intelligent meeting minutes and other scenarios.

**Modelscope[audio] only support on Linux-x86_64 for now，not available in Mac and Windows.**

Paraformer webserver provides an HTTP interface build with sanic framework of python.
* transcribe


## Quick start
Docker hub: https://hub.docker.com/r/lovemefan/paraformer-webserver

```bash
# for gpu
docker run -d --gpus all -p 9000:9000 lovemefan/paraformer-webserver:cuda-11.2

# for cpu

docker run -d -p 9000:9000 lovemefan/paraformer-webserver:amd64
```

## RUN
```bash
git clone https://github.com/lovemefan/Paraformer-webserver
cd Paraformer-webserver
pip install "modelscope[audio]" -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html -i https://mirrors.aliyun.com/pypi/simple 
pip install -r requirement.txt -i https://mirrors.aliyun.com/pypi/simple
gunicorn --bind 0.0.0.0:9000 --workers 1  backend.app:app -k uvicorn.workers.UvicornWorker
```

## Docker build
### FOR CPU
```bash
# Build Image
docker build -f Dockerfile-cpu -t paraformer-webserver-cpu .

# Run Container
docker run -d -p 9000:9000 paraformer-webserver-cpu
```

### FOR GPU
```bash
# Build Image
docker build -f Dockerfile-gpu -t paraformer-webserver-gpu .

# Run Container
docker run -d --gpus all -p 9000:9000 paraformer-webserver-gpu

```


## Usage
use 16000hz, 16bit, mono format of wav file
```bash
curl --location --request POST --X POST 'http://localhost:9000/v1/api/speech/recognition' \
--form 'audio=@/path/audio.wav'
```
Response

```json
{
	"message": "Success",
	"code": 200,
	"data": {
		"text": "搜狐娱乐北京朝阳法院通告分别产出八十八万吨九十四万吨鹰眼打下的真"
	}
}
```
