#!/usr/bin/env python3
"""
详细调试Luma Ray2 API调用
"""

import boto3
import json
import logging
from botocore.exceptions import ClientError

# 启用详细日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_api_call():
    client = boto3.client('bedrock-runtime', region_name='us-west-2')
    
    # 尝试不同的参数组合
    test_cases = [
        {
            "name": "最简单格式",
            "params": {
                "modelId": "luma.ray-v2:0",
                "modelInput": json.dumps({"prompt": "a cat"}),
                "outputDataConfig": {
                    "s3OutputDataConfig": {
                        "s3Uri": "s3://s3-demo-zy/luma_test/"
                    }
                }
            }
        },
        {
            "name": "带基本参数",
            "params": {
                "modelId": "luma.ray-v2:0",
                "modelInput": json.dumps({
                    "prompt": "a cat",
                    "duration": "5s"
                }),
                "outputDataConfig": {
                    "s3OutputDataConfig": {
                        "s3Uri": "s3://s3-demo-zy/luma_test/"
                    }
                }
            }
        },
        {
            "name": "完整参数",
            "params": {
                "modelId": "luma.ray-v2:0",
                "modelInput": json.dumps({
                    "prompt": "Ultraman fighting Godzilla in the ocean",
                    "aspect_ratio": "16:9",
                    "duration": "5s",
                    "resolution": "720p",
                    "loop": False
                }),
                "outputDataConfig": {
                    "s3OutputDataConfig": {
                        "s3Uri": "s3://s3-demo-zy/luma_test/"
                    }
                }
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"🧪 测试 {i}: {test_case['name']}")
        print(f"{'='*60}")
        
        params = test_case['params']
        print(f"📝 参数:")
        print(f"   modelId: {params['modelId']}")
        print(f"   modelInput: {params['modelInput']}")
        print(f"   outputDataConfig: {json.dumps(params['outputDataConfig'], indent=4)}")
        
        try:
            print(f"\n🚀 发送请求...")
            response = client.start_async_invoke(**params)
            
            print(f"✅ 成功!")
            print(f"📋 响应: {json.dumps(response, indent=2, default=str)}")
            return response['invocationArn']
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            print(f"❌ 失败!")
            print(f"   错误代码: {error_code}")
            print(f"   错误消息: {error_message}")
            
            # 打印完整的错误响应
            print(f"   完整响应: {json.dumps(e.response, indent=2, default=str)}")
            
        except Exception as e:
            print(f"❌ 未知错误: {str(e)}")
            print(f"   错误类型: {type(e)}")
    
    return None

if __name__ == "__main__":
    print("🔍 详细调试Luma Ray2 API调用")
    print("=" * 60)
    
    arn = debug_api_call()
    
    if arn:
        print(f"\n🎉 找到可用的API格式!")
        print(f"📋 任务ARN: {arn}")
        print(f"⏳ 任务已启动，请等待2-5分钟生成完成")
    else:
        print(f"\n❌ 所有格式都失败了")
        print(f"💡 可能需要检查:")
        print(f"   1. 模型访问权限")
        print(f"   2. S3桶权限")
        print(f"   3. API参数格式")
        print(f"   4. 区域设置")
