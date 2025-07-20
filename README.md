# AWS Bedrock Luma Ray2 视频生成工具

使用AWS Bedrock调用Luma Ray2模型生成视频的Python工具。

## 🚀 功能特性

- ✅ **文本到视频生成**: 根据文字描述生成视频
- ✅ **图片到视频生成**: 基于图片生成动态视频
- ✅ **本地图片支持**: 支持本地图片文件作为输入
- ✅ **S3图片支持**: 支持S3存储的图片作为输入
- ✅ **双关键帧**: 支持起始帧+结束帧的视频生成
- ✅ **详细日志**: 启动时输出prompt和参数信息
- ✅ **异步处理**: 支持任务状态检查和等待完成

## 📋 环境要求

```bash
pip install -r requirements.txt
```

## 🔧 配置

### 1. AWS凭证配置
```bash
aws configure
# 或设置环境变量
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-west-2
```

### 2. S3桶权限设置
```bash
# 确保S3桶存在
aws s3 mb s3://s3-demo-zy --region us-west-2

# 设置桶策略允许Bedrock写入
aws s3api put-bucket-policy --bucket s3-demo-zy --policy '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock.amazonaws.com"
      },
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::s3-demo-zy/luma_test/*"
    }
  ]
}'
```

## 💻 使用示例

### 基础使用

```python
from luma_ray2_client import LumaRay2Client

# 初始化客户端
client = LumaRay2Client()

# 1. 文本到视频
arn = client.text_to_video(
    prompt="一只小猫在花园里玩耍",
    s3_output_uri="s3://s3-demo-zy/luma_test/"
)

# 2. 本地图片到视频
arn = client.image_to_video(
    prompt="让这张图片动起来",
    s3_output_uri="s3://s3-demo-zy/luma_test/",
    start_image_path="./my_photo.jpg"  # 本地文件
)

# 3. S3图片到视频
arn = client.image_to_video(
    prompt="添加动态效果",
    s3_output_uri="s3://s3-demo-zy/luma_test/",
    start_image_path="s3://my-bucket/image.jpg"  # S3路径
)

# 4. 等待任务完成
result = client.wait_for_completion(arn)
```

### 高级参数

```python
# 自定义参数
arn = client.text_to_video(
    prompt="城市夜景，车流如河",
    s3_output_uri="s3://s3-demo-zy/luma_test/",
    aspect_ratio="16:9",    # 宽高比
    duration="9s",          # 视频时长 (5s/9s)
    resolution="720p",      # 分辨率 (540p/720p)
    loop=False             # 是否循环
)

# 双关键帧视频
arn = client.image_to_video(
    prompt="从白天过渡到夜晚",
    s3_output_uri="s3://s3-demo-zy/luma_test/",
    start_image_path="./day.jpg",      # 起始帧
    end_image_path="s3://bucket/night.jpg",  # 结束帧
    duration="9s"
)
```

## 📊 支持的参数

| 参数 | 类型 | 可选值 | 默认值 | 说明 |
|------|------|--------|--------|------|
| `aspect_ratio` | string | "1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21" | "16:9" | 视频宽高比 |
| `duration` | string | "5s", "9s" | "5s" | 视频时长 |
| `resolution` | string | "540p", "720p" | "720p" | 视频分辨率 |
| `loop` | boolean | true, false | false | 是否循环播放 |

## 🖼️ 图片输入支持

### 本地文件
```python
# 支持的本地路径格式
"./image.jpg"
"/path/to/image.png"
"~/Pictures/photo.jpeg"
```

### S3路径
```python
# 支持的S3路径格式
"s3://bucket-name/image.jpg"
"s3://my-bucket/folder/subfolder/image.png"
```

## 📝 日志输出示例

```
=== 启动文本到视频生成任务 ===
Prompt: 一只橙色的小猫在绿色的草地上追逐蝴蝶，阳光透过树叶洒下斑驳的光影
参数配置:
  - 宽高比: 16:9
  - 时长: 5s
  - 分辨率: 720p
  - 循环播放: False
  - 输出路径: s3://s3-demo-zy/luma_test/
✅ 文本到视频任务已启动: arn:aws:bedrock:us-west-2:123456789012:async-invoke/xxxxx
```

## 🔍 任务管理

```python
# 检查任务状态
status = client.get_job_status(arn)
print(f"状态: {status['status']}")

# 列出所有任务
jobs = client.list_jobs(max_results=10)
for job in jobs['asyncInvokes']:
    print(f"{job['status']}: {job['invocationArn']}")

# 等待任务完成（带超时）
result = client.wait_for_completion(arn, max_wait_time=600)
```

## ⚠️ 注意事项

1. **处理时间**: 5秒视频约需2-5分钟，9秒视频约需4-8分钟
2. **图片要求**: 
   - 支持格式: JPEG, PNG
   - 最小尺寸: 512x512像素
   - 最大尺寸: 4096x4096像素
3. **提示文本**: 长度限制1-5000字符
4. **费用**: 按生成的视频时长计费
5. **区域**: 目前支持us-west-2区域

## 🚨 故障排除

| 问题 | 解决方案 |
|------|----------|
| 任务失败 | 检查S3桶权限和区域设置 |
| 图片访问错误 | 确保图片格式正确且路径可访问 |
| 参数错误 | 验证宽高比、时长等参数值 |
| 权限不足 | 检查IAM权限配置 |

## 📞 快速开始

运行示例代码：
```bash
python examples.py
```

## 📁 项目结构

```
aws-bedrock-luma-ray2/
├── luma_ray2_client.py    # 主要客户端类
├── examples.py            # 使用示例
├── requirements.txt       # 依赖包
├── README.md             # 项目说明
├── .gitignore           # Git忽略文件
└── LICENSE              # 许可证
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License
