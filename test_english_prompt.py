#!/usr/bin/env python3
"""
使用英文prompt测试Luma Ray2 API
"""

import boto3
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_english_prompt():
    client = boto3.client('bedrock-runtime', region_name='us-west-2')
    
    # 使用英文prompt
    model_input = {
        "prompt": "Ultraman and Godzilla fighting in the deep blue ocean, massive water splashes, Ultraman shooting light beams, Godzilla breathing atomic fire, rolling waves, spectacular battle scene"
    }
    
    output_config = {
        "s3OutputDataConfig": {
            "s3Uri": "s3://s3-demo-zy/luma_test/"
        }
    }
    
    try:
        logger.info("测试英文prompt...")
        logger.info(f"Prompt: {model_input['prompt']}")
        
        response = client.start_async_invoke(
            modelId="luma.ray-v2:0",
            modelInput=json.dumps(model_input),
            outputDataConfig=output_config
        )
        
        logger.info("✅ 英文prompt成功!")
        logger.info(f"任务ARN: {response['invocationArn']}")
        return response['invocationArn']
        
    except Exception as e:
        logger.error(f"❌ 英文prompt失败: {str(e)}")
        return None

if __name__ == "__main__":
    arn = test_english_prompt()
    if arn:
        print(f"\n🎉 视频生成任务已启动!")
        print(f"📋 任务ARN: {arn}")
        print(f"⏳ 请等待2-5分钟生成完成...")
    else:
        print("\n❌ 任务启动失败")
