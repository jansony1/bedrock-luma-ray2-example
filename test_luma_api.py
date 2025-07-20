#!/usr/bin/env python3
"""
测试Luma Ray2 API调用格式
"""

import boto3
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_luma_api():
    client = boto3.client('bedrock-runtime', region_name='us-west-2')
    
    # 根据AWS文档的正确格式
    model_input = {
        "prompt": "奥特曼和哥斯拉在深蓝色的海洋中激烈战斗，巨大的水花四溅，奥特曼发出光线攻击，哥斯拉喷射原子吐息，海浪翻滚，场面震撼壮观",
        "aspect_ratio": "16:9",
        "duration": "5s",
        "resolution": "720p",
        "loop": False
    }
    
    output_config = {
        "s3OutputDataConfig": {
            "s3Uri": "s3://s3-demo-zy/luma_test/"
        }
    }
    
    try:
        logger.info("测试API调用...")
        logger.info(f"Model Input: {json.dumps(model_input, indent=2)}")
        logger.info(f"Output Config: {json.dumps(output_config, indent=2)}")
        
        response = client.start_async_invoke(
            modelId="luma.ray-v2:0",
            modelInput=json.dumps(model_input),
            outputDataConfig=output_config
        )
        
        logger.info("✅ API调用成功!")
        logger.info(f"Response: {response}")
        return response['invocationArn']
        
    except Exception as e:
        logger.error(f"❌ API调用失败: {str(e)}")
        
        # 尝试更简单的格式
        logger.info("尝试简化的请求格式...")
        simple_input = {
            "prompt": "a cat playing in a garden"
        }
        
        try:
            response = client.start_async_invoke(
                modelId="luma.ray-v2:0",
                modelInput=json.dumps(simple_input),
                outputDataConfig=output_config
            )
            logger.info("✅ 简化格式成功!")
            logger.info(f"Response: {response}")
            return response['invocationArn']
        except Exception as e2:
            logger.error(f"❌ 简化格式也失败: {str(e2)}")
            return None

if __name__ == "__main__":
    test_luma_api()
