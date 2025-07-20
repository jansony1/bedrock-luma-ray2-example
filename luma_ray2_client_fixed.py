#!/usr/bin/env python3
"""
AWS Bedrock Luma Ray2 模型调用客户端 - 修复版
使用原始HTTP请求解决boto3参数传递问题
"""

import boto3
import json
import time
import base64
import logging
import requests
from typing import Optional, Dict, Any
from pathlib import Path
from urllib.parse import urlparse
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LumaRay2Client:
    """Luma Ray2 模型客户端 - 修复版"""
    
    def __init__(self, region_name: str = 'us-west-2'):
        """
        初始化客户端
        
        Args:
            region_name: AWS区域名称
        """
        self.region_name = region_name
        self.bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=region_name
        )
        self.s3_client = boto3.client(
            's3',
            region_name=region_name
        )
        self.model_id = "luma.ray-v2:0"
        
        # 获取AWS凭证用于原始HTTP请求
        session = boto3.Session()
        self.credentials = session.get_credentials()
        self.endpoint_url = f"https://bedrock-runtime.{region_name}.amazonaws.com/async-invoke"
    
    def _make_raw_request(self, payload: Dict) -> str:
        """使用原始HTTP请求调用API"""
        body = json.dumps(payload)
        
        # 创建AWS请求对象
        request = AWSRequest(
            method='POST',
            url=self.endpoint_url,
            data=body,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        
        # 签名请求
        SigV4Auth(self.credentials, 'bedrock', self.region_name).add_auth(request)
        
        # 发送请求
        response = requests.post(
            self.endpoint_url,
            data=body,
            headers=dict(request.headers)
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['invocationArn']
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
    
    def _is_s3_path(self, path: str) -> bool:
        """检查路径是否为S3路径"""
        return path.startswith('s3://')
    
    def _parse_s3_path(self, s3_path: str) -> tuple:
        """解析S3路径，返回bucket和key"""
        parsed = urlparse(s3_path)
        bucket = parsed.netloc
        key = parsed.path.lstrip('/')
        return bucket, key
    
    def _download_s3_image(self, s3_path: str) -> bytes:
        """从S3下载图片数据"""
        try:
            bucket, key = self._parse_s3_path(s3_path)
            logger.info(f"从S3下载图片: s3://{bucket}/{key}")
            
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            return response['Body'].read()
        except Exception as e:
            logger.error(f"从S3下载图片失败: {str(e)}")
            raise
    
    def _encode_image_from_path(self, image_path: str) -> str:
        """从本地文件或S3路径编码图片为base64"""
        try:
            if self._is_s3_path(image_path):
                # S3路径
                image_data = self._download_s3_image(image_path)
                return base64.b64encode(image_data).decode('utf-8')
            else:
                # 本地文件路径
                logger.info(f"读取本地图片: {image_path}")
                with open(image_path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"图片编码失败: {str(e)}")
            raise
    
    def text_to_video(
        self,
        prompt: str,
        s3_output_uri: str,
        aspect_ratio: str = "16:9",
        duration: str = "5s",
        resolution: str = "720p",
        loop: bool = False
    ) -> str:
        """
        文本到视频生成
        
        Args:
            prompt: 视频描述文本 (1-5000字符)
            s3_output_uri: S3输出路径
            aspect_ratio: 宽高比 ("1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21")
            duration: 视频时长 ("5s", "9s")
            resolution: 分辨率 ("540p", "720p")
            loop: 是否循环播放
            
        Returns:
            任务ARN
        """
        if not (1 <= len(prompt) <= 5000):
            raise ValueError("提示文本长度必须在1-5000字符之间")
        
        # 输出启动信息
        logger.info("=== 启动文本到视频生成任务 ===")
        logger.info(f"Prompt: {prompt}")
        logger.info(f"参数配置:")
        logger.info(f"  - 宽高比: {aspect_ratio}")
        logger.info(f"  - 时长: {duration}")
        logger.info(f"  - 分辨率: {resolution}")
        logger.info(f"  - 循环播放: {loop}")
        logger.info(f"  - 输出路径: {s3_output_uri}")
        
        # 构建请求负载
        model_input = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "duration": duration,
            "resolution": resolution,
            "loop": loop
        }
        
        payload = {
            "modelId": self.model_id,
            "modelInput": model_input,
            "outputDataConfig": {
                "s3OutputDataConfig": {
                    "s3Uri": s3_output_uri
                }
            }
        }
        
        try:
            invocation_arn = self._make_raw_request(payload)
            logger.info(f"✅ 文本到视频任务已启动: {invocation_arn}")
            return invocation_arn
            
        except Exception as e:
            logger.error(f"❌ 启动文本到视频任务失败: {str(e)}")
            raise
    
    def image_to_video(
        self,
        prompt: str,
        s3_output_uri: str,
        start_image_path: Optional[str] = None,
        end_image_path: Optional[str] = None,
        start_image_base64: Optional[str] = None,
        end_image_base64: Optional[str] = None,
        aspect_ratio: str = "16:9",
        duration: str = "5s",
        resolution: str = "720p",
        loop: bool = False
    ) -> str:
        """
        图片到视频生成
        
        Args:
            prompt: 视频描述文本
            s3_output_uri: S3输出路径
            start_image_path: 起始帧图片路径（支持本地文件或s3://路径）
            end_image_path: 结束帧图片路径（支持本地文件或s3://路径）
            start_image_base64: 起始帧图片base64数据
            end_image_base64: 结束帧图片base64数据
            aspect_ratio: 宽高比
            duration: 视频时长
            resolution: 分辨率
            loop: 是否循环播放
            
        Returns:
            任务ARN
        """
        # 输出启动信息
        logger.info("=== 启动图片到视频生成任务 ===")
        logger.info(f"Prompt: {prompt}")
        logger.info(f"参数配置:")
        logger.info(f"  - 宽高比: {aspect_ratio}")
        logger.info(f"  - 时长: {duration}")
        logger.info(f"  - 分辨率: {resolution}")
        logger.info(f"  - 循环播放: {loop}")
        logger.info(f"  - 输出路径: {s3_output_uri}")
        
        if start_image_path:
            logger.info(f"  - 起始帧图片: {start_image_path}")
        if end_image_path:
            logger.info(f"  - 结束帧图片: {end_image_path}")
        
        model_input = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "duration": duration,
            "resolution": resolution,
            "loop": loop,
            "keyframes": {}
        }
        
        # 处理起始帧
        if start_image_path or start_image_base64:
            if start_image_path:
                logger.info("正在处理起始帧图片...")
                start_image_base64 = self._encode_image_from_path(start_image_path)
            
            model_input["keyframes"]["frame0"] = {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": start_image_base64
                }
            }
        
        # 处理结束帧
        if end_image_path or end_image_base64:
            if end_image_path:
                logger.info("正在处理结束帧图片...")
                end_image_base64 = self._encode_image_from_path(end_image_path)
            
            model_input["keyframes"]["frame1"] = {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": end_image_base64
                }
            }
        
        payload = {
            "modelId": self.model_id,
            "modelInput": model_input,
            "outputDataConfig": {
                "s3OutputDataConfig": {
                    "s3Uri": s3_output_uri
                }
            }
        }
        
        try:
            invocation_arn = self._make_raw_request(payload)
            logger.info(f"✅ 图片到视频任务已启动: {invocation_arn}")
            return invocation_arn
            
        except Exception as e:
            logger.error(f"❌ 启动图片到视频任务失败: {str(e)}")
            raise
    
    def get_job_status(self, invocation_arn: str) -> Dict[str, Any]:
        """
        获取任务状态
        
        Args:
            invocation_arn: 任务ARN
            
        Returns:
            任务状态信息
        """
        try:
            response = self.bedrock_runtime.get_async_invoke(
                invocationArn=invocation_arn
            )
            return response
        except Exception as e:
            logger.error(f"获取任务状态失败: {str(e)}")
            raise
    
    def wait_for_completion(
        self,
        invocation_arn: str,
        max_wait_time: int = 600,
        check_interval: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        等待任务完成
        
        Args:
            invocation_arn: 任务ARN
            max_wait_time: 最大等待时间（秒）
            check_interval: 检查间隔（秒）
            
        Returns:
            最终任务状态
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                status_response = self.get_job_status(invocation_arn)
                status = status_response['status']
                
                logger.info(f"任务状态: {status}")
                
                if status == 'Completed':
                    logger.info("视频生成完成！")
                    output_uri = status_response.get('outputDataConfig', {}).get('s3OutputDataConfig', {}).get('s3Uri')
                    if output_uri:
                        logger.info(f"输出位置: {output_uri}")
                    return status_response
                    
                elif status == 'Failed':
                    error_msg = status_response.get('failureMessage', '未知错误')
                    logger.error(f"任务失败: {error_msg}")
                    return status_response
                    
                elif status in ['InProgress', 'Submitted']:
                    logger.info(f"任务进行中，{check_interval}秒后再次检查...")
                    time.sleep(check_interval)
                    
                else:
                    logger.warning(f"未知状态: {status}")
                    time.sleep(check_interval)
                    
            except Exception as e:
                logger.error(f"检查任务状态时出错: {str(e)}")
                time.sleep(check_interval)
        
        logger.warning("等待超时")
        return None
    
    def list_jobs(self, max_results: int = 10) -> Dict[str, Any]:
        """
        列出异步任务
        
        Args:
            max_results: 最大返回结果数
            
        Returns:
            任务列表
        """
        try:
            response = self.bedrock_runtime.list_async_invokes(
                maxResults=max_results
            )
            return response
        except Exception as e:
            logger.error(f"列出任务失败: {str(e)}")
            raise


# 便捷函数
def quick_text_to_video(prompt: str, output_path: str = "s3://s3-demo-zy/luma_test/") -> str:
    """快速文本到视频生成"""
    client = LumaRay2Client()
    return client.text_to_video(prompt, output_path)


def quick_image_to_video(prompt: str, image_path: str, output_path: str = "s3://s3-demo-zy/luma_test/") -> str:
    """快速图片到视频生成"""
    client = LumaRay2Client()
    return client.image_to_video(prompt, output_path, start_image_path=image_path)
