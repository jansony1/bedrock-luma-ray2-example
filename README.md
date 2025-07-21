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
- ✅ **AWS原生方法**: 使用boto3标准API调用

## 📋 环境要求

```bash
pip install -r requirements.txt
```

**重要**: 需要boto3 >= 1.39.0 以支持异步API

## 🔧 配置

### 1. AWS凭证配置
```bash
aws configure
# 或设置环境变量
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-west-2
```

### 2. 申请Luma模型访问权限
1. 打开AWS控制台 → Amazon Bedrock
2. 选择区域: `us-west-2`
3. Model access → Request model access
4. 勾选: Luma AI → Ray v2
5. 提交申请并等待批准

### 3. S3桶权限设置
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

### 快速开始

```python
from luma_ray2_client import LumaRay2Client

# 初始化客户端
client = LumaRay2Client()

# 1. 文本到视频
arn = client.text_to_video(
    prompt="Ultraman fighting Godzilla in the ocean",
    s3_output_uri="s3://s3-demo-zy/luma_test/"
)

# 2. 等待完成
result = client.wait_for_completion(arn)
```

### 高级用法

```python
# 图片到视频
arn = client.image_to_video(
    prompt="让这张图片动起来",
    s3_output_uri="s3://s3-demo-zy/luma_test/",
    start_image_path="./my_photo.jpg",  # 本地文件
    duration="5s",
    resolution="720p"
)

# S3图片到视频
arn = client.image_to_video(
    prompt="添加动态效果",
    s3_output_uri="s3://s3-demo-zy/luma_test/",
    start_image_path="s3://my-bucket/image.jpg"  # S3路径
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
"./image.jpg"           # 相对路径
"/path/to/image.png"    # 绝对路径
"~/Pictures/photo.jpeg" # 用户目录
```

### S3路径
```python
"s3://bucket-name/image.jpg"
"s3://my-bucket/folder/subfolder/image.png"
```

## 📝 日志输出示例

```
=== 启动文本到视频生成任务 ===
调用方法: boto3标准方法
Prompt: Ultraman fighting Godzilla in the ocean
参数配置:
  - 宽高比: 16:9
  - 时长: 5s
  - 分辨率: 720p
  - 循环播放: False
  - 输出路径: s3://s3-demo-zy/luma_test/
🔧 使用boto3标准方法调用...
✅ boto3方法调用成功!
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
6. **模型权限**: 需要在Bedrock控制台申请Luma Ray2访问权限

## 🚨 故障排除

| 问题 | 解决方案 |
|------|----------|
| ValidationException | 检查模型访问权限是否已申请 |
| 任务失败 | 检查S3桶权限和区域设置 |
| 图片访问错误 | 确保图片格式正确且路径可访问 |
| 参数错误 | 验证宽高比、时长等参数值 |
| 权限不足 | 检查IAM权限配置 |
| ThrottlingException | 等待一段时间后重试 |

详细解决方案请查看 [SOLUTION.md](SOLUTION.md)

## 📞 快速开始

### 🚀 方法1: 一键自动设置（推荐新手）
```bash
# 克隆项目
git clone https://github.com/jansony1/bedrock-luma-ray2-example.git
cd bedrock-luma-ray2-example

# 一键设置环境（自动安装依赖、检查配置、创建S3桶等）
./setup.sh

# 运行奥特曼vs哥斯拉示例
python3 generate_ultraman_godzilla_boto3.py
```

### ⚡ 方法2: 手动设置（适合有经验用户）
```bash
# 安装依赖
pip install -r requirements.txt

# 配置AWS凭证（如果未配置）
aws configure

# 运行示例
python3 generate_ultraman_godzilla_boto3.py
```

### 🎬 方法3: 运行完整示例集合
```bash
python3 examples.py
```

## 📁 项目结构

```
aws-bedrock-luma-ray2/
├── luma_ray2_client.py              # 🎯 主客户端（AWS原生方法）
├── setup.sh                        # 🚀 一键环境设置脚本（推荐首次使用）
├── generate_ultraman_godzilla_boto3.py  # 🎬 奥特曼vs哥斯拉示例
├── examples.py                      # 📚 完整使用示例
├── requirements.txt                 # 📦 依赖包
├── README.md                       # 📖 项目说明
├── SOLUTION.md                     # 🔧 问题解决指南
├── METHOD_COMPARISON.md            # 📊 方法对比文档（历史参考）
├── .gitignore                      # Git忽略文件
└── LICENSE                         # MIT许可证
```

## 🎊 成功案例

我们已经成功生成了多个视频：
- 🐉 威严的龙飞越中世纪城堡（日落时分）
- 🦸‍♂️ 奥特曼大战哥斯拉海战场面
- 🌊 各种海洋和自然场景

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License
