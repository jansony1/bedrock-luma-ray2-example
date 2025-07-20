#!/usr/bin/env python3
"""
尝试原始HTTP请求格式调用Luma Ray2
"""

import boto3
import json
import logging
import requests
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_raw_http_request():
    """使用原始HTTP请求测试"""
    
    # 获取AWS凭证
    session = boto3.Session()
    credentials = session.get_credentials()
    
    # 构建请求
    url = "https://bedrock-runtime.us-west-2.amazonaws.com/async-invoke"
    
    # 尝试不同的请求体格式
    test_payloads = [
        {
            "name": "标准格式",
            "payload": {
                "modelId": "luma.ray-v2:0",
                "modelInput": {
                    "prompt": "Ultraman fighting Godzilla in the ocean"
                },
                "outputDataConfig": {
                    "s3OutputDataConfig": {
                        "s3Uri": "s3://s3-demo-zy/luma_test/"
                    }
                }
            }
        },
        {
            "name": "字符串化modelInput",
            "payload": {
                "modelId": "luma.ray-v2:0",
                "modelInput": json.dumps({
                    "prompt": "Ultraman fighting Godzilla in the ocean"
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
            "payload": {
                "modelId": "luma.ray-v2:0",
                "modelInput": {
                    "prompt": "Ultraman fighting Godzilla in the ocean",
                    "aspect_ratio": "16:9",
                    "duration": "5s",
                    "resolution": "720p",
                    "loop": False
                },
                "outputDataConfig": {
                    "s3OutputDataConfig": {
                        "s3Uri": "s3://s3-demo-zy/luma_test/"
                    }
                }
            }
        }
    ]
    
    for i, test_case in enumerate(test_payloads, 1):
        print(f"\n{'='*60}")
        print(f"🧪 原始HTTP测试 {i}: {test_case['name']}")
        print(f"{'='*60}")
        
        payload = test_case['payload']
        body = json.dumps(payload)
        
        print(f"📝 请求体: {body}")
        
        try:
            # 创建AWS请求对象
            request = AWSRequest(
                method='POST',
                url=url,
                data=body,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            
            # 签名请求
            SigV4Auth(credentials, 'bedrock', 'us-west-2').add_auth(request)
            
            # 发送请求
            print(f"🚀 发送原始HTTP请求...")
            response = requests.post(
                url,
                data=body,
                headers=dict(request.headers)
            )
            
            print(f"📊 响应状态: {response.status_code}")
            print(f"📋 响应头: {dict(response.headers)}")
            print(f"📄 响应体: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 成功! 任务ARN: {result.get('invocationArn', 'N/A')}")
                return result.get('invocationArn')
            else:
                print(f"❌ 失败: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ 请求异常: {str(e)}")
    
    return None

def test_boto3_with_different_regions():
    """测试不同区域的boto3调用"""
    regions = ['us-west-2', 'us-east-1', 'eu-west-1']
    
    for region in regions:
        print(f"\n{'='*60}")
        print(f"🌍 测试区域: {region}")
        print(f"{'='*60}")
        
        try:
            client = boto3.client('bedrock-runtime', region_name=region)
            
            # 检查该区域是否有Luma模型
            bedrock = boto3.client('bedrock', region_name=region)
            models = bedrock.list_foundation_models(byProvider='Luma AI')
            
            if not models['modelSummaries']:
                print(f"⚠️  该区域没有Luma模型")
                continue
                
            print(f"✅ 该区域有 {len(models['modelSummaries'])} 个Luma模型")
            
            # 尝试调用
            response = client.start_async_invoke(
                modelId="luma.ray-v2:0",
                modelInput=json.dumps({
                    "prompt": "Ultraman fighting Godzilla in the ocean"
                }),
                outputDataConfig={
                    "s3OutputDataConfig": {
                        "s3Uri": "s3://s3-demo-zy/luma_test/"
                    }
                }
            )
            
            print(f"✅ 成功! 任务ARN: {response['invocationArn']}")
            return response['invocationArn']
            
        except Exception as e:
            print(f"❌ 失败: {str(e)}")
    
    return None

def main():
    print("🔍 原始HTTP请求测试Luma Ray2")
    print("=" * 60)
    
    # 测试原始HTTP请求
    arn = test_raw_http_request()
    
    if not arn:
        # 测试不同区域
        print(f"\n🌍 尝试不同区域...")
        arn = test_boto3_with_different_regions()
    
    if arn:
        print(f"\n🎉 找到可用方法! 任务ARN: {arn}")
        print(f"⏳ 任务已启动，请等待2-5分钟生成完成")
    else:
        print(f"\n❌ 所有方法都失败了")
        print(f"💡 建议联系AWS技术支持或检查控制台网络请求")

if __name__ == "__main__":
    main()
