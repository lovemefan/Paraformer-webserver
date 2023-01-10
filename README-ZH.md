# Paraformer webserver
Paraformer是达摩院语音团队提出的一种高效的非自回归端到端语音识别框架，多个公开数据集上取得SOTA效果。
该项目为Paraformer中文通用语音识别模型，采用工业级数万小时的标注音频进行模型训练，保证了模型的通用识别效果。
模型可以被应用于语音输入法、语音导航、智能会议纪要等场景。

**现阶段modelscope[audio]只能在Linux-x86_64运行，不支持Mac和Windows。**


本项目使用sanic为该语音识别框架搭建一个简单的http接口服务，并提供语音转写服务。

第一次调用接口时才会加载模型，所以第一次调用会比较慢，待改进。

## 快速使用
Docker hub地址: https://hub.docker.com/r/lovemefan/paraformer-webserver

```bash
# for gpu
docker run -d --gpus all -p 9000:9000 lovemefan/paraformer-webserver:cuda-11.2.0

# for cpu

docker run -d -p 9000:9000 lovemefan/paraformer-webserver:amd64

```

## 启动项目
```bash
git clone https://github.com/lovemefan/Paraformer-webserver
cd Paraformer-webserver
pip install "modelscope[audio]" -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html -i https://mirrors.aliyun.com/pypi/simple 
pip install -r requirement.txt -i https://mirrors.aliyun.com/pypi/simple
gunicorn --bind 0.0.0.0:9000 --workers 1  backend.app:app -k uvicorn.workers.UvicornWorker
```

## 构建镜像
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


## 接口使用
当前接口仅支持 16000hz, 16比特, 单通道wav格式的音频
```bash
curl --location --request POST --X POST 'http://localhost:9000/v1/api/speech/recognition' \
--form 'audio=@/path/audio.wav'
```


