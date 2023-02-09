# Paraformer webserver
[English readme](README-EN.md)

Paraformer是达摩院语音团队提出的一种高效的非自回归端到端语音识别框架，多个公开数据集上取得SOTA效果，缺点是该模型没有标点符号。
该项目为Paraformer中文通用语音识别模型，采用工业级数万小时的标注音频进行模型训练，保证了模型的通用识别效果。
模型可以被应用于语音输入法、语音导航、智能会议纪要等场景。


本项目使用sanic为该语音识别框架搭建一个简单的http接口服务，并提供语音转写服务。
模型使用官方pytorch模型并导出为onnx模型
目前支持：
* pytorch GPU 只支持cuda,x86, linux
* pytorch CPU 只支持x86, linux
* ONNX CPU 目前只在linux和mac os上测试，支持x86cpu和aarch64的m1芯片

## CER
时间：2022.11

| 测试集                                | 领域             | paraformer | bilibili | 思必驰 | 阿里 | 百度 | 讯飞 | 微软 | 腾讯 | 依图 |
| ------------------------------------- | ---------------- | ---------- |----------| ------ | ---- | ---- | ---- | ---- | ---- | ---- |
| 直播带货 李佳琪薇娅 （770, 0.9H）     | 电商、美妆       | 6.38       | 6.26     | 10.1   | 8.2  | 16.7 | 10.5 | 7.2  | 6.6  | 7.3  |
| 新闻联播 （5069, 9H）                 | 时政             | 0.65       | 0.61     | 1      | 0.8  | 1.6  | 1    | 0.3  | 1.1  | 0.8  |
| 访谈 鲁豫有约 （2993, 3H）            | 工作、说话       | 3.59       | 2.9      | 3.3    | 3.5  | 5.9  | 3.7  | 3.1  | 3.4  | 3.0  |
| 场馆演讲罗振宇跨年 （1311, 2.7H）     | 社会、人文、商业 | 1.97       | 1.59     | 1.7    | 1.5  | 3.2  | 2.4  | 1.3  | 1.7  | 1.5  |
| 在线教育 李永乐 （3148, 4.4H）        | 科普             | 2.6        | 1.49     | 2.2    | 2    | 6.9  | 2.2  | 1.6  | 1.9  | 1.8  |
| 播客 创业内幕 （2251, 4.2H）          | 创业、产品、投资 | 4.7        | 3.59     | 4.2    | 3.3  | 7.3  | 4.1  | 4.2  | 3.8  | 3.7  |
| 线下培训 老罗语录 （884,1.3H）        | 段子、做人       | 4.6        | 3.78     | 6.5    | 4.9  | 14.1 | 6.6  | 6.2  | 5.5  | 4.8  |
| 直播 王者荣耀 （1561, 1.6H）          | 游戏             | 6.73       | 5.88     | 8.1    | 6.5  | 10.3 | 8.9  | 6.9  | 6.1  | 6.9  |
| 电视节目 天下足球 （1683, 2.7H）      | 足球             | 1.28       | 0.98     | 1.5    | 1.6  | 5.4  | 2.1  | 1    | 3.2  | 0.8  |
| 播客故事FM （3466, 4.5H）             | 人生故事、见闻   | 3.53       | 3.26     | 3.8    | 3.3  | 5.6  | 4.1  | 4.2  | 3.7  | 3.3  |
| 罗翔   法考（1053, 4H）               |                  | 2.02       | 1.92     | 2.9    | 2.4  | 5.6  | 3.4  | 1.9  | 2.2  | 1.7  |
| 张雪峰 在线教育考研(1170, 3.5H)       |                  | 3.41       | 2.12     | 3.2    | 4.1  | 9.3  | 3.5  | 3.3  | 2.7  | 2.6  |
| 谷阿莫 短视频 影剪(1321, 2.5H)        |                  | 3.89       | 3.07     | 4.0    | 3.5  | 7.7  | 4.6  | 5.4  | 3.0  | 2.8  |
| 琼斯爱生活 美食&烹饪(856, 2H)         |                  | 4.68       | 3.74     | 6.4    | 6.6  | 13.2 | 6.1  | 5.9  | 4.6  | 4.0  |
| 单田芳 评书白眉大侠(1168, 2.5H)       |                  | 5.2        | 4.79     | 9.3    | 7.4  | 15.4 | 10.7 | 8.3  | 5.7  | 5.5  |
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
wget https://github.com/lovemefan/Paraformer-webserver/releases/download/v2.0.1/paraformer.onnx -o backend/onnx/paraformer.onnx
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

