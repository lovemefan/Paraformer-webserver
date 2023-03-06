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
测试时间：2022.11 部分数据来源：https://github.com/SpeechColab/Leaderboard

| 测试集                            | 领域             | paraformer | bilibili | 思必驰 | 阿里 | 百度  | 讯飞 | 微软 | 腾讯 | 依图 |
| --------------------------------- | ---------------- | ---------- | -------- | ------ | ---- | ----- | ---- | ---- | ---- | ---- |
| 直播带货 李佳琪薇娅 （770, 0.9H） | 电商、美妆       | 6.38       | 6.26     | 7.47   | 4.72 | 16.72 | 9.7  | 6.15 | 6.55 | 7.33 |
| 新闻联播 （5069, 9H）             | 时政             | 0.65       | 0.61     | 1.26   | 0.43 | 1.56  | 0.86 | 0.28 | 1.09 | 0.76 |
| 访谈 鲁豫有约 （2993, 3H）        | 工作、说话       | 3.59       | 2.9      | 2.46   | 2.7  | 5.86  | 3.35 | 2.82 | 3.43 | 2.94 |
| 场馆演讲罗振宇跨年 （1311, 2.7H） | 社会、人文、商业 | 1.97       | 1.59     | 2.49   | 1.36 | 3.23  | 2.16 | 1.14 | 1.72 | 1.49 |
| 在线教育 李永乐 （3148, 4.4H）    | 科普             | 2.6        | 1.49     | 1.66   | 1.27 | 6.89  | 2.1  | 1.45 | 1.86 | 1.81 |
| 播客 创业内幕 （2251, 4.2H）      | 创业、产品、投资 | 4.7        | 3.59     | 4.58   | 3.9  | 14.17 | 5.77 | 4.6  | 3.8  | 3.7  |
| 线下培训 老罗语录 （884,1.3H）    | 段子、做人       | 4.6        | 3.78     | 4.58   | 3.9  | 14.17 | 5.77 | 4.6  | 5.51 | 4.76 |
| 直播 王者荣耀 （1561, 1.6H）      | 游戏             | 6.73       | 5.88     | 5.17   | 4.72 | 10.34 | 8.2  | 5.9  | 6.09 | 6.92 |
| 电视节目 天下足球 （1683, 2.7H）  | 足球             | 1.28       | 0.98     | 2.21   | 0.94 | 5.38  | 1.78 | 0.9  | 3.22 | 0.83 |
| 播客故事FM （3466, 4.5H）         | 人生故事、见闻   | 3.53       | 3.26     | 2.68   | 2.44 | 7.28  | 4.01 | 3.61 | 3.79 | 3.67 |
| 罗翔   法考（1053, 4H）           | 法律 法考        | 2.02       | 1.92     | 3.76   | 1.22 | 5.55  | 2.98 | 1.21 | 2.23 | 1.65 |
| 张雪峰 在线教育考研(1170, 3.5H)   | 考研 高校报考    | 3.41       | 2.12     | 3.61   | 1.87 | 9.34  | 3.24 | 2.22 | 2.66 | 2.61 |
| 谷阿莫 短视频 影剪(1321, 2.5H)    | 美食、烹饪       | 3.89       | 3.07     | 4.67   | 2.07 | 7.65  | 4.12 | 4.27 | 2.98 | 2.81 |
| 琼斯爱生活 美食&烹饪(856, 2H)     | 美食、烹饪       | 4.68       | 3.74     | 8.45   | 3.15 | 13.17 | 5.44 | 3.34 | 4.63 | 3.99 |
| 单田芳 评书白眉大侠(1168, 2.5H)   | 江湖、武侠       | 5.2        | 4.79     | 14.19  | 3.16 | 15.42 | 9.77 | 5.86 | 5.71 | 5.45 |
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
docker run -d -p 9000:9000 -v /path/logs:/app/backend/logs lovemefan/paraformer-webserver:onnx-aarch64

```

## 启动项目
```bash
git clone https://github.com/lovemefan/Paraformer-webserver
cd Paraformer-webserver
wget https://github.com/lovemefan/Paraformer-webserver/releases/download/v2.0.1/paraformer.onnx -o backend/onnx/paraformer.onnx
pip install -r requirements-cpu.txt -i https://mirrors.aliyun.com/pypi/simple
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

