#!/usr/bin/env python3
"""
按照AWS官方文档格式测试Luma Ray2
"""

import boto3
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_official_format():
    client = boto3.client('bedrock-runtime', region_name='us-west-2')
    
    # 完全按照官方文档的格式
    test_cases = [
        {
            "name": "基础文本到视频",
            "modelInput": {
                "prompt": "an old lady laughing underwater, wearing a scuba diving suit"
            }
        },
        {
            "name": "简单汽车示例",
            "modelInput": {
                "prompt": "a car",
                "resolution": "720p",
                "duration": "5s"
            }
        },
        {
            "name": "奥特曼vs哥斯拉",
            "modelInput": {
                "prompt": "Ultraman fighting Godzilla in the ocean",
                "aspect_ratio": "16:9",
                "duration": "5s",
                "resolution": "720p",
                "loop": False
            }
        }
    ]
    
    output_config = {
        "s3OutputDataConfig": {
            "s3Uri": "s3://s3-demo-zy/luma_test/"
        }
    }
    
    for test_case in test_cases:
        print(f"\n🧪 测试: {test_case['name']}")
        print(f"📝 输入: {json.dumps(test_case['modelInput'], indent=2)}")
        
        try:
            response = client.start_async_invoke(
                modelId="luma.ray-v2:0",
                modelInput=json.dumps(test_case['modelInput']),
                outputDataConfig=output_config
            )
            
            print(f"✅ 成功! ARN: {response['invocationArn']}")
            return response['invocationArn']
            
        except Exception as e:
            print(f"❌ 失败: {str(e)}")
            continue
    
    return None

if __name__ == "__main__":
    arn = test_official_format()
    if arn:
        print(f"\n🎉 找到可用格式! 任务ARN: {arn}")
        
        # 等待任务完成
        client = boto3.client('bedrock-runtime', region_name='us-west-2')
        print(f"⏳ 开始等待任务完成...")
        
        import time
        max_wait = 600  # 10分钟
        check_interval = 30  # 30秒检查一次
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                status_response = client.get_async_invoke(invocationArn=arn)
                status = status_response['status']
                
                print(f"📊 当前状态: {status}")
                
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
                    print(f"⏳ 任务进行中，{check_interval}秒后再次检查...")
                    time.sleep(check_interval)
                else:
                    print(f"❓ 未知状态: {status}")
                    time.sleep(check_interval)
                    
            except Exception as e:
                print(f"❌ 检查状态失败: {e}")
                time.sleep(check_interval)
        else:
            print(f"⏰ 等待超时")
    else:
        print(f"\n❌ 所有格式都失败了")
