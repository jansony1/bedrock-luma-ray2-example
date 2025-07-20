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
- ✅ **双调用方法**: boto3标准方法 + 原始HTTP请求备用
- ✅ **自动回退**: 智能选择最佳调用方法

## 🎬 **最新更新**

### **重大修复**: boto3方法现已完全可用！
- 🔧 修正了`modelInput`参数传递格式
- ✅ boto3标准方法现在是推荐的调用方式
- 🔄 保留原始HTTP请求作为备用方案
- 📊 添加了完整的方法对比和测试套件

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
from luma_ray2_client_complete import LumaRay2Client

# 初始化客户端（推荐方式）
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
# 使用特定调用方法
client_boto3 = LumaRay2Client(use_raw_http=False)  # 仅boto3
client_http = LumaRay2Client(use_raw_http=True)    # 仅HTTP请求

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

## 🎯 **调用方法对比**

| 方法 | 状态 | 推荐度 | 说明 |
|------|------|--------|------|
| **boto3标准方法** | ✅ 可用 | ⭐⭐⭐⭐⭐ | 官方SDK，稳定可靠 |
| **原始HTTP请求** | ⚠️ 备用 | ⭐⭐⭐ | 特殊情况使用 |
| **自动回退机制** | ✅ 推荐 | ⭐⭐⭐⭐⭐ | 最佳实践 |

详细对比请查看 [METHOD_COMPARISON.md](METHOD_COMPARISON.md)

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
调用方法: boto3标准方法（自动回退）
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

### 方法1: 运行奥特曼vs哥斯拉示例
```bash
python3 generate_ultraman_godzilla_boto3.py
```

### 方法2: 运行完整示例
```bash
python3 examples.py
```

### 方法3: 测试两种调用方法
```bash
python3 test_both_methods.py
```

## 📁 项目结构

```
aws-bedrock-luma-ray2/
├── luma_ray2_client.py              # 原始客户端
├── luma_ray2_client_complete.py     # 完整客户端（推荐）
├── examples.py                      # 基础使用示例
├── generate_ultraman_godzilla_boto3.py  # 奥特曼vs哥斯拉示例
├── test_both_methods.py             # 方法对比测试
├── requirements.txt                 # 依赖包
├── setup.sh                        # 快速安装脚本
├── README.md                       # 项目说明
├── METHOD_COMPARISON.md            # 方法对比文档
├── SOLUTION.md                     # 问题解决指南
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
