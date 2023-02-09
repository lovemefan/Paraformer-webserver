# Paraformer webserver
[English readme](README-EN.md)

Paraformer是达摩院语音团队提出的一种高效的非自回归端到端语音识别框架，多个公开数据集上取得SOTA效果，缺点是该模型没有标点符号。
该项目为Paraformer中文通用语音识别模型，采用工业级数万小时的标注音频进行模型训练，保证了模型的通用识别效果。
模型可以被应用于语音输入法、语音导航、智能会议纪要等场景。


本项目使用sanic为该语音识别框架搭建一个简单的http接口服务，并提供语音转写服务。
模型使用官方pytorch模型并导出为onnx模型
目前支持：
* pytorch GPU 只cuda,x86, linux
* pytorch CPU 只支持x86, linux
* ONNX CPU 目前只在linux和mac os上测试，支持x86cpu和aarch64的m1芯片


## 快速使用
Docker hub地址: https://hub.docker.com/r/lovemefan/paraformer-webserver

```bash
# for gpu with pytorch
docker run -d --gpus all -p 9000:9000 lovemefan/paraformer-webserver:cuda-11.2.0

# for cpu with pytorch
docker run -d -p 9000:9000 lovemefan/paraformer-webserver:amd64

# for cpu with onnx
docker run -d -p 9000:9000 -v /path/logs:/app/backend/logs lovemefan/paraformer-webserver:onnx-amd

# for mac m1 with onnx
docker run -d -p 9000:9000 -v /path/logs:/app/backend/logs lovemefan/paraformer-webserver:onnx-arrach64

```

## 启动项目
```bash
git clone https://github.com/lovemefan/Paraformer-webserver
cd Paraformer-webserver
wget https://github.com/lovemefan/Paraformer-webserver/releases/download/v2.0/paraformer.onnx -o backend/onnx/paraformer.onnx
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
curl --location --request POST -X POST 'http://localhost:9000/v1/api/speech/recognition' \
--form 'audio=@/path/audio.wav'
```
响应:
```json
{
	"message": "Success",
	"code": 200,
	"data": {
		"text": "搜狐娱乐北京朝阳法院通告分别产出八十八万吨九十四万吨鹰眼打下的真"
	}
}
```

