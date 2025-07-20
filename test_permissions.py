#!/usr/bin/env python3
"""
测试AWS权限和服务可用性
"""

import boto3
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_permissions():
    print("🔍 测试AWS权限和服务可用性")
    print("=" * 50)
    
    # 1. 测试基本AWS权限
    try:
        sts = boto3.client('sts', region_name='us-west-2')
        identity = sts.get_caller_identity()
        print(f"✅ AWS身份验证成功")
        print(f"   用户: {identity.get('Arn', 'N/A')}")
        print(f"   账户: {identity.get('Account', 'N/A')}")
    except Exception as e:
        print(f"❌ AWS身份验证失败: {e}")
        return False
    
    # 2. 测试S3权限
    try:
        s3 = boto3.client('s3', region_name='us-west-2')
        s3.head_bucket(Bucket='s3-demo-zy')
        print(f"✅ S3桶访问正常: s3-demo-zy")
        
        # 测试写入权限
        s3.put_object(
            Bucket='s3-demo-zy',
            Key='luma_test/test_permissions.txt',
            Body=b'Permission test'
        )
        print(f"✅ S3写入权限正常")
    except Exception as e:
        print(f"❌ S3权限测试失败: {e}")
        return False
    
    # 3. 测试Bedrock基本权限
    try:
        bedrock = boto3.client('bedrock', region_name='us-west-2')
        models = bedrock.list_foundation_models(byProvider='Luma AI')
        print(f"✅ Bedrock基本权限正常")
        print(f"   找到Luma模型数量: {len(models['modelSummaries'])}")
    except Exception as e:
        print(f"❌ Bedrock基本权限失败: {e}")
        return False
    
    # 4. 测试Bedrock Runtime权限
    try:
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')
        # 尝试列出异步任务
        jobs = bedrock_runtime.list_async_invokes(maxResults=1)
        print(f"✅ Bedrock Runtime权限正常")
        print(f"   当前异步任务数: {len(jobs.get('asyncInvokes', []))}")
    except Exception as e:
        print(f"❌ Bedrock Runtime权限失败: {e}")
        return False
    
    # 5. 测试具体的Luma模型调用（最小化参数）
    try:
        print(f"\n🧪 测试Luma模型调用...")
        
        # 最简单的请求
        response = bedrock_runtime.start_async_invoke(
            modelId="luma.ray-v2:0",
            modelInput='{"prompt": "a simple cat"}',
            outputDataConfig={
                "s3OutputDataConfig": {
                    "s3Uri": "s3://s3-demo-zy/luma_test/"
                }
            }
        )
        
        print(f"✅ Luma模型调用成功!")
        print(f"   任务ARN: {response['invocationArn']}")
        return response['invocationArn']
        
    except Exception as e:
        print(f"❌ Luma模型调用失败: {e}")
        
        # 检查错误类型
        error_str = str(e)
        if "AccessDenied" in error_str:
            print("💡 提示: 可能需要申请Luma模型的访问权限")
        elif "ValidationException" in error_str:
            print("💡 提示: 请求格式可能有问题")
        elif "ResourceNotFound" in error_str:
            print("💡 提示: 模型在当前区域不可用")
        
        return False

if __name__ == "__main__":
    result = test_permissions()
    if result:
        print(f"\n🎉 所有测试通过! 任务ARN: {result}")
    else:
        print(f"\n❌ 测试失败，请检查权限配置")
