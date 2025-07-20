#!/usr/bin/env python3
"""
测试两种调用方法的对比
1. boto3标准方法（修正版）
2. 原始HTTP请求方法
"""

from luma_ray2_client_complete import LumaRay2Client
import logging
import time

# 设置日志级别
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_boto3_method():
    """测试boto3标准方法"""
    print("\n" + "="*60)
    print("🧪 测试1: boto3标准方法（根据官方文档修正）")
    print("="*60)
    
    try:
        # 使用boto3方法
        client = LumaRay2Client(use_raw_http=False)
        
        prompt = "A majestic dragon flying over a medieval castle at sunset"
        s3_output_uri = "s3://s3-demo-zy/luma_test/"
        
        print(f"🎯 测试prompt: {prompt}")
        
        invocation_arn = client.text_to_video(
            prompt=prompt,
            s3_output_uri=s3_output_uri,
            aspect_ratio="16:9",
            duration="5s",
            resolution="720p",
            loop=False
        )
        
        print(f"✅ boto3方法成功!")
        print(f"📋 任务ARN: {invocation_arn}")
        return invocation_arn
        
    except Exception as e:
        print(f"❌ boto3方法失败: {str(e)}")
        return None

def test_raw_http_method():
    """测试原始HTTP请求方法"""
    print("\n" + "="*60)
    print("🧪 测试2: 原始HTTP请求方法")
    print("="*60)
    
    try:
        # 使用原始HTTP请求方法
        client = LumaRay2Client(use_raw_http=True)
        
        prompt = "A peaceful lake with swans swimming at dawn, misty atmosphere"
        s3_output_uri = "s3://s3-demo-zy/luma_test/"
        
        print(f"🎯 测试prompt: {prompt}")
        
        invocation_arn = client.text_to_video(
            prompt=prompt,
            s3_output_uri=s3_output_uri,
            aspect_ratio="16:9",
            duration="5s",
            resolution="720p",
            loop=False
        )
        
        print(f"✅ 原始HTTP方法成功!")
        print(f"📋 任务ARN: {invocation_arn}")
        return invocation_arn
        
    except Exception as e:
        print(f"❌ 原始HTTP方法失败: {str(e)}")
        return None

def test_auto_fallback():
    """测试自动回退机制"""
    print("\n" + "="*60)
    print("🧪 测试3: 自动回退机制（boto3 -> HTTP）")
    print("="*60)
    
    try:
        # 使用自动回退（默认）
        client = LumaRay2Client(use_raw_http=False)
        
        prompt = "Ultraman and Godzilla epic battle in the ocean with massive waves"
        s3_output_uri = "s3://s3-demo-zy/luma_test/"
        
        print(f"🎯 测试prompt: {prompt}")
        
        invocation_arn = client.text_to_video(
            prompt=prompt,
            s3_output_uri=s3_output_uri,
            aspect_ratio="16:9",
            duration="5s",
            resolution="720p",
            loop=False
        )
        
        print(f"✅ 自动回退机制成功!")
        print(f"📋 任务ARN: {invocation_arn}")
        return invocation_arn
        
    except Exception as e:
        print(f"❌ 自动回退机制失败: {str(e)}")
        return None

def monitor_task(invocation_arn: str, task_name: str):
    """监控任务状态"""
    if not invocation_arn:
        return
        
    print(f"\n⏳ 监控任务: {task_name}")
    print(f"📋 ARN: {invocation_arn}")
    
    client = LumaRay2Client()
    
    for i in range(10):  # 最多检查10次
        try:
            status_response = client.get_job_status(invocation_arn)
            status = status_response['status']
            
            print(f"📊 检查 {i+1}/10: {status}")
            
            if status == 'Completed':
                print(f"🎉 {task_name} 完成!")
                output_uri = status_response.get('outputDataConfig', {}).get('s3OutputDataConfig', {}).get('s3Uri')
                if output_uri:
                    print(f"📁 输出位置: {output_uri}")
                break
            elif status == 'Failed':
                error_msg = status_response.get('failureMessage', '未知错误')
                print(f"❌ {task_name} 失败: {error_msg}")
                break
            elif status in ['InProgress', 'Submitted']:
                print(f"⏳ 进行中，30秒后再次检查...")
                time.sleep(30)
            else:
                print(f"❓ 未知状态: {status}")
                time.sleep(30)
                
        except Exception as e:
            print(f"❌ 状态检查失败: {e}")
            time.sleep(30)
    else:
        print(f"⏰ {task_name} 监控超时")

def main():
    print("🔍 Luma Ray2 两种调用方法对比测试")
    print("=" * 60)
    
    # 存储任务ARN
    tasks = {}
    
    # 测试boto3方法
    tasks['boto3'] = test_boto3_method()
    
    # 测试原始HTTP方法
    tasks['raw_http'] = test_raw_http_method()
    
    # 测试自动回退
    tasks['auto_fallback'] = test_auto_fallback()
    
    # 总结测试结果
    print("\n" + "="*60)
    print("📊 测试结果总结")
    print("="*60)
    
    success_count = 0
    for method, arn in tasks.items():
        if arn:
            print(f"✅ {method}: 成功 - {arn}")
            success_count += 1
        else:
            print(f"❌ {method}: 失败")
    
    print(f"\n📈 成功率: {success_count}/{len(tasks)} ({success_count/len(tasks)*100:.1f}%)")
    
    # 监控所有成功的任务
    if success_count > 0:
        print(f"\n⏳ 开始监控所有成功的任务...")
        for method, arn in tasks.items():
            if arn:
                monitor_task(arn, method)
    
    print(f"\n🎊 测试完成!")

if __name__ == "__main__":
    main()
