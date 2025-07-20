#!/usr/bin/env python3
"""
权限确认后的Luma Ray2测试
尝试不同的API调用格式
"""

import boto3
import json
import logging
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_different_formats():
    client = boto3.client('bedrock-runtime', region_name='us-west-2')
    
    # 测试不同的调用格式
    test_cases = [
        {
            "name": "格式1: 不转义JSON字符串",
            "params": {
                "modelId": "luma.ray-v2:0",
                "modelInput": {"prompt": "Ultraman fighting Godzilla in the ocean"},
                "outputDataConfig": {
                    "s3OutputDataConfig": {
                        "s3Uri": "s3://s3-demo-zy/luma_test/"
                    }
                }
            }
        },
        {
            "name": "格式2: 使用body参数",
            "params": {
                "modelId": "luma.ray-v2:0",
                "body": json.dumps({"prompt": "Ultraman fighting Godzilla in the ocean"}),
                "outputDataConfig": {
                    "s3OutputDataConfig": {
                        "s3Uri": "s3://s3-demo-zy/luma_test/"
                    }
                }
            }
        },
        {
            "name": "格式3: 完整参数不转义",
            "params": {
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
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"🧪 测试 {i}: {test_case['name']}")
        print(f"{'='*60}")
        
        params = test_case['params']
        print(f"📝 参数: {json.dumps(params, indent=2, default=str)}")
        
        try:
            print(f"\n🚀 发送请求...")
            
            # 尝试不同的调用方式
            if 'body' in params:
                # 使用body参数
                response = client.start_async_invoke(
                    modelId=params['modelId'],
                    body=params['body'],
                    outputDataConfig=params['outputDataConfig']
                )
            elif isinstance(params['modelInput'], dict):
                # modelInput作为字典
                response = client.start_async_invoke(
                    modelId=params['modelId'],
                    modelInput=json.dumps(params['modelInput']),
                    outputDataConfig=params['outputDataConfig']
                )
            else:
                # 标准调用
                response = client.start_async_invoke(**params)
            
            print(f"✅ 成功!")
            print(f"📋 任务ARN: {response['invocationArn']}")
            return response['invocationArn']
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            print(f"❌ 失败!")
            print(f"   错误代码: {error_code}")
            print(f"   错误消息: {error_message}")
            
        except Exception as e:
            print(f"❌ 未知错误: {str(e)}")
    
    return None

def test_invoke_model_sync():
    """尝试同步调用看是否有更详细的错误信息"""
    client = boto3.client('bedrock-runtime', region_name='us-west-2')
    
    print(f"\n{'='*60}")
    print(f"🧪 测试同步调用 (可能不支持，但能获得更详细错误)")
    print(f"{'='*60}")
    
    try:
        response = client.invoke_model(
            modelId="luma.ray-v2:0",
            body=json.dumps({
                "prompt": "Ultraman fighting Godzilla in the ocean"
            })
        )
        print(f"✅ 同步调用成功: {response}")
    except Exception as e:
        print(f"❌ 同步调用失败: {str(e)}")
        print(f"💡 这是预期的，因为Luma模型只支持异步调用")

def main():
    print("🔍 权限确认后的Luma Ray2测试")
    print("=" * 60)
    
    # 首先确认基本信息
    try:
        sts = boto3.client('sts', region_name='us-west-2')
        identity = sts.get_caller_identity()
        print(f"✅ AWS身份: {identity.get('Arn', 'N/A')}")
        
        bedrock = boto3.client('bedrock', region_name='us-west-2')
        models = bedrock.list_foundation_models(byProvider='Luma AI')
        print(f"✅ Luma模型可用: {len(models['modelSummaries'])} 个")
        
    except Exception as e:
        print(f"❌ 基本检查失败: {e}")
        return
    
    # 测试同步调用获取更多错误信息
    test_invoke_model_sync()
    
    # 测试不同的异步调用格式
    arn = test_different_formats()
    
    if arn:
        print(f"\n🎉 找到可用格式! 任务ARN: {arn}")
        print(f"⏳ 开始监控任务状态...")
        
        # 监控任务状态
        client = boto3.client('bedrock-runtime', region_name='us-west-2')
        import time
        
        for i in range(20):  # 最多检查20次，每次30秒
            try:
                status_response = client.get_async_invoke(invocationArn=arn)
                status = status_response['status']
                
                print(f"📊 状态检查 {i+1}/20: {status}")
                
                if status == 'Completed':
                    print(f"🎉 视频生成完成!")
                    output_uri = status_response.get('outputDataConfig', {}).get('s3OutputDataConfig', {}).get('s3Uri')
                    if output_uri:
                        print(f"📁 输出位置: {output_uri}")
                    break
                elif status == 'Failed':
                    error_msg = status_response.get('failureMessage', '未知错误')
                    print(f"❌ 任务失败: {error_msg}")
                    break
                elif status in ['InProgress', 'Submitted']:
                    print(f"⏳ 任务进行中，30秒后再次检查...")
                    time.sleep(30)
                else:
                    print(f"❓ 未知状态: {status}")
                    time.sleep(30)
                    
            except Exception as e:
                print(f"❌ 状态检查失败: {e}")
                time.sleep(30)
        else:
            print(f"⏰ 监控超时，请稍后手动检查任务状态")
    else:
        print(f"\n❌ 所有格式都失败了")
        print(f"💡 建议:")
        print(f"   1. 检查控制台中的具体调用格式")
        print(f"   2. 确认模型权限是否完全激活")
        print(f"   3. 尝试在控制台中生成相同的视频")

if __name__ == "__main__":
    main()
