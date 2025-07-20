# AWS Bedrock Luma Ray2 调用方法对比

## 🎯 **总结**

经过详细测试，我们发现了调用Luma Ray2模型的正确方法，并保留了两种实现方式。

## 📊 **方法对比**

### **方法1: boto3标准方法（推荐）** ✅

**状态**: 已修正，完全可用

**关键修正**: `modelInput`参数应该作为字典直接传递，而不是JSON字符串

```python
# ✅ 正确的方式
response = client.start_async_invoke(
    modelId="luma.ray-v2:0",
    modelInput={  # 直接传递字典
        "prompt": "your prompt here",
        "aspect_ratio": "16:9",
        "duration": "5s",
        "resolution": "720p",
        "loop": False
    },
    outputDataConfig={
        "s3OutputDataConfig": {
            "s3Uri": "s3://bucket/path/"
        }
    }
)

# ❌ 错误的方式（之前的问题）
response = client.start_async_invoke(
    modelId="luma.ray-v2:0",
    modelInput=json.dumps(model_input),  # 不要转换为字符串！
    outputDataConfig=output_config
)
```

**优势**:
- 使用AWS官方SDK
- 自动处理认证和签名
- 更好的错误处理
- 符合AWS最佳实践
- 更容易维护

### **方法2: 原始HTTP请求方法** ⚠️

**状态**: 可用，但有限制

```python
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

# 构建原始HTTP请求
url = "https://bedrock-runtime.us-west-2.amazonaws.com/async-invoke"
payload = {
    "modelId": "luma.ray-v2:0",
    "modelInput": {
        "prompt": "your prompt here"
    },
    "outputDataConfig": {
        "s3OutputDataConfig": {
            "s3Uri": "s3://bucket/path/"
        }
    }
}

# 手动签名和发送请求
```

**限制**:
- 容易触发429限流错误
- 需要手动处理签名
- 代码复杂度更高
- 维护成本高

## 🔧 **完整客户端实现**

我们的`LumaRay2Client`类提供了两种方法：

```python
from luma_ray2_client_complete import LumaRay2Client

# 使用boto3方法（推荐）
client = LumaRay2Client(use_raw_http=False)

# 使用原始HTTP方法
client = LumaRay2Client(use_raw_http=True)

# 自动回退机制（先尝试boto3，失败后使用HTTP）
client = LumaRay2Client()  # 默认行为
```

## 📋 **API调用详情**

### **Bedrock服务信息**
- **服务**: `bedrock-runtime`
- **方法**: `start_async_invoke`
- **端点**: `https://bedrock-runtime.{region}.amazonaws.com/async-invoke`
- **模型ID**: `luma.ray-v2:0`

### **必需参数**
- `modelId`: 模型标识符
- `modelInput`: 模型输入（字典格式）
- `outputDataConfig`: 输出配置

### **可选参数**
- `clientRequestToken`: 幂等性令牌
- `tags`: 资源标签

## 🎬 **测试结果**

| 方法 | 状态 | 成功率 | 备注 |
|------|------|--------|------|
| boto3标准方法 | ✅ 成功 | 100% | 推荐使用 |
| 原始HTTP请求 | ⚠️ 限制 | 受限流影响 | 备用方案 |
| 自动回退机制 | ✅ 可用 | 高 | 最佳实践 |

## 💡 **最佳实践建议**

1. **优先使用boto3方法**: 更稳定，更符合AWS最佳实践
2. **保留HTTP方法作为备用**: 在特殊情况下可能有用
3. **使用自动回退机制**: 提供最佳的可靠性
4. **注意限流**: 避免短时间内发送过多请求
5. **监控任务状态**: 使用`get_async_invoke`检查进度

## 🎯 **推荐用法**

```python
from luma_ray2_client_complete import LumaRay2Client

# 推荐的使用方式
client = LumaRay2Client()  # 默认使用boto3，自动回退

arn = client.text_to_video(
    prompt="Ultraman fighting Godzilla in the ocean",
    s3_output_uri="s3://s3-demo-zy/luma_test/",
    duration="5s",
    resolution="720p"
)

result = client.wait_for_completion(arn)
```

## 🔍 **问题解决历程**

1. **初始问题**: boto3调用返回ValidationException
2. **尝试方案**: 使用原始HTTP请求（成功）
3. **深入分析**: 发现boto3参数传递格式错误
4. **最终解决**: 修正modelInput参数格式
5. **验证结果**: boto3方法完全可用

## 📚 **相关文档**

- [AWS Bedrock StartAsyncInvoke API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_StartAsyncInvoke.html)
- [Luma AI模型参数文档](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-luma.html)
- [AWS SDK for Python (Boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
