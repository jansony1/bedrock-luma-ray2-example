#!/usr/bin/env python3
"""
AWS Bedrock Luma Ray2 模型调用客户端
使用AWS原生boto3方法调用Luma Ray2模型生成视频
"""

import boto3
import json
import time
import base64
import logging
# import requests  # HTTP方法需要的依赖，已注释
from typing import Optional, Dict, Any
from pathlib import Path
from urllib.parse import urlparse
# from botocore.auth import SigV4Auth  # HTTP方法需要的依赖，已注释
# from botocore.awsrequest import AWSRequest  # HTTP方法需要的依赖，已注释

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LumaRay2Client:
    """Luma Ray2 模型客户端"""
    
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
        
        # HTTP方法需要的凭证获取，已注释
        # session = boto3.Session()
        # self.credentials = session.get_credentials()
    
    def _make_boto3_request(self, model_input: Dict, output_config: Dict) -> str:
        """使用boto3标准方法调用API"""
        try:
            logger.info("🔧 使用boto3标准方法调用...")
            
            # 根据官方API文档，modelInput应该是JSON value，不是字符串
            response = self.bedrock_runtime.start_async_invoke(
                modelId=self.model_id,
                modelInput=model_input,  # 直接传递字典，不转换为字符串
                outputDataConfig=output_config
            )
            
            logger.info("✅ boto3方法调用成功!")
            return response['invocationArn']
            
        except Exception as e:
            logger.error(f"❌ boto3方法失败: {str(e)}")
            raise
    
    # ========== HTTP方法实现（已注释，保留作为参考） ==========
    # def _make_raw_request(self, payload: Dict) -> str:
    #     """使用原始HTTP请求调用API"""
    #     try:
    #         logger.info("🔧 使用原始HTTP请求方法调用...")
    #         
    #         # 构建请求URL
    #         url = f"https://bedrock-runtime.{self.region_name}.amazonaws.com/async-invoke"
    #         
    #         # 构建请求头
    #         headers = {
    #             'Content-Type': 'application/json',
    #             'Accept': 'application/json'
    #         }
    #         
    #         # 创建AWS请求对象
    #         request = AWSRequest(
    #             method='POST',
    #             url=url,
    #             data=json.dumps(payload),
    #             headers=headers
    #         )
    #         
    #         # 使用SigV4签名
    #         SigV4Auth(self.credentials, 'bedrock', self.region_name).add_auth(request)
    #         
    #         # 发送请求
    #         response = requests.post(
    #             url,
    #             data=request.body,
    #             headers=dict(request.headers)
    #         )
    #         
    #         if response.status_code == 200:
    #             result = response.json()
    #             logger.info("✅ 原始HTTP请求调用成功!")
    #             return result['invocationArn']
    #         else:
    #             error_msg = f"HTTP请求失败: {response.status_code} - {response.text}"
    #             logger.error(f"❌ {error_msg}")
    #             raise Exception(error_msg)
    #             
    #     except Exception as e:
    #         logger.error(f"❌ 原始HTTP请求失败: {str(e)}")
    #         raise
    
    def _upload_image_to_s3(self, image_path: str) -> str:
        """
        上传本地图片到S3并返回S3 URI
        
        Args:
            image_path: 本地图片路径
            
        Returns:
            S3 URI
        """
        try:
            # 生成唯一的S3键名
            import uuid
            file_extension = Path(image_path).suffix
            s3_key = f"temp_images/{uuid.uuid4()}{file_extension}"
            bucket_name = "s3-demo-zy"
            
            # 上传文件
            self.s3_client.upload_file(image_path, bucket_name, s3_key)
            s3_uri = f"s3://{bucket_name}/{s3_key}"
            
            logger.info(f"📤 图片已上传到S3: {s3_uri}")
            return s3_uri
            
        except Exception as e:
            logger.error(f"❌ 图片上传失败: {str(e)}")
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
        logger.info(f"调用方法: boto3标准方法")
        logger.info(f"Prompt: {prompt}")
        logger.info(f"参数配置:")
        logger.info(f"  - 宽高比: {aspect_ratio}")
        logger.info(f"  - 时长: {duration}")
        logger.info(f"  - 分辨率: {resolution}")
        logger.info(f"  - 循环播放: {loop}")
        logger.info(f"  - 输出路径: {s3_output_uri}")
        
        # 构建模型输入（作为字典，不是字符串）
        model_input = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "duration": duration,
            "resolution": resolution,
            "loop": loop
        }
        
        output_config = {
            "s3OutputDataConfig": {
                "s3Uri": s3_output_uri
            }
        }
        
        # 使用boto3标准方法
        invocation_arn = self._make_boto3_request(model_input, output_config)
        logger.info(f"✅ 文本到视频任务已启动: {invocation_arn}")
        return invocation_arn
        
        # ========== HTTP方法调用（已注释，保留作为参考） ==========
        # # 构建HTTP请求payload
        # payload = {
        #     "modelId": self.model_id,
        #     "modelInput": model_input,
        #     "outputDataConfig": output_config
        # }
        # 
        # # 使用原始HTTP请求方法
        # invocation_arn = self._make_raw_request(payload)
        # logger.info(f"✅ 文本到视频任务已启动: {invocation_arn}")
        # return invocation_arn
    
    def image_to_video(
        self,
        prompt: str,
        s3_output_uri: str,
        start_image_path: str,
        end_image_path: Optional[str] = None,
        aspect_ratio: str = "16:9",
        duration: str = "5s",
        resolution: str = "720p",
        loop: bool = False
    ) -> str:
        """
        图片到视频生成
        
        Args:
            prompt: 视频描述文本 (1-5000字符)
            s3_output_uri: S3输出路径
            start_image_path: 起始图片路径（本地文件或S3路径）
            end_image_path: 结束图片路径（可选，本地文件或S3路径）
            aspect_ratio: 宽高比
            duration: 视频时长
            resolution: 分辨率
            loop: 是否循环播放
            
        Returns:
            任务ARN
        """
        if not (1 <= len(prompt) <= 5000):
            raise ValueError("提示文本长度必须在1-5000字符之间")
        
        # 输出启动信息
        logger.info("=== 启动图片到视频生成任务 ===")
        logger.info(f"调用方法: boto3标准方法")
        logger.info(f"Prompt: {prompt}")
        logger.info(f"参数配置:")
        logger.info(f"  - 起始图片: {start_image_path}")
        if end_image_path:
            logger.info(f"  - 结束图片: {end_image_path}")
        logger.info(f"  - 宽高比: {aspect_ratio}")
        logger.info(f"  - 时长: {duration}")
        logger.info(f"  - 分辨率: {resolution}")
        logger.info(f"  - 循环播放: {loop}")
        logger.info(f"  - 输出路径: {s3_output_uri}")
        
        # 读取并编码图片为base64
        def encode_image_to_base64(image_path_or_uri):
            if image_path_or_uri.startswith('s3://'):
                # 如果是S3路径，先下载到本地
                import tempfile
                import os
                from urllib.parse import urlparse
                
                parsed = urlparse(image_path_or_uri)
                bucket = parsed.netloc
                key = parsed.path.lstrip('/')
                
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    self.s3_client.download_file(bucket, key, tmp_file.name)
                    with open(tmp_file.name, 'rb') as f:
                        image_data = f.read()
                    os.unlink(tmp_file.name)
            else:
                # 本地文件
                with open(image_path_or_uri, 'rb') as f:
                    image_data = f.read()
            
            import base64
            return base64.b64encode(image_data).decode('utf-8')
        
        def get_media_type(image_path):
            ext = Path(image_path).suffix.lower()
            if ext in ['.jpg', '.jpeg']:
                return 'image/jpeg'
            elif ext == '.png':
                return 'image/png'
            else:
                return 'image/jpeg'  # 默认
        
        # 编码起始图片
        start_image_b64 = encode_image_to_base64(start_image_path)
        start_media_type = get_media_type(start_image_path)
        
        # 构建模型输入
        model_input = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "duration": duration,
            "resolution": resolution,
            "loop": loop,
            "keyframes": {
                "frame0": {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": start_media_type,
                        "data": start_image_b64
                    }
                }
            }
        }
        
        # 如果有结束图片，添加到关键帧
        if end_image_path:
            end_image_b64 = encode_image_to_base64(end_image_path)
            end_media_type = get_media_type(end_image_path)
            model_input["keyframes"]["frame1"] = {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": end_media_type,
                    "data": end_image_b64
                }
            }
        
        output_config = {
            "s3OutputDataConfig": {
                "s3Uri": s3_output_uri
            }
        }
        
        # 使用boto3标准方法
        invocation_arn = self._make_boto3_request(model_input, output_config)
        logger.info(f"✅ 图片到视频任务已启动: {invocation_arn}")
        return invocation_arn
        
        # ========== HTTP方法调用（已注释，保留作为参考） ==========
        # # 构建HTTP请求payload
        # payload = {
        #     "modelId": self.model_id,
        #     "modelInput": model_input,
        #     "outputDataConfig": output_config
        # }
        # 
        # # 使用原始HTTP请求方法
        # invocation_arn = self._make_raw_request(payload)
        # logger.info(f"✅ 图片到视频任务已启动: {invocation_arn}")
        # return invocation_arn
    
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
            logger.error(f"❌ 获取任务状态失败: {str(e)}")
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
            任务完成后的状态信息，超时返回None
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                status_info = self.get_job_status(invocation_arn)
                status = status_info.get('status', 'Unknown')
                
                logger.info(f"任务状态: {status}")
                
                if status == 'Completed':
                    logger.info("视频生成完成！")
                    # 获取输出信息
                    output_config = status_info.get('outputDataConfig', {})
                    s3_output = output_config.get('s3OutputDataConfig', {})
                    output_uri = s3_output.get('s3Uri', '')
                    if output_uri:
                        logger.info(f"输出位置: {output_uri}")
                    return status_info
                elif status == 'Failed':
                    logger.error("任务执行失败")
                    return status_info
                elif status in ['InProgress', 'Submitted']:
                    logger.info(f"任务进行中，{check_interval}秒后再次检查...")
                    time.sleep(check_interval)
                else:
                    logger.warning(f"未知状态: {status}")
                    time.sleep(check_interval)
                    
            except Exception as e:
                logger.error(f"检查任务状态时出错: {str(e)}")
                time.sleep(check_interval)
        
        logger.warning(f"等待超时（{max_wait_time}秒）")
        return None
    
    def list_jobs(self, max_results: int = 10) -> Dict[str, Any]:
        """
        列出异步调用任务
        
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
            logger.error(f"❌ 获取任务列表失败: {str(e)}")
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


if __name__ == "__main__":
    # 简单测试
    print("🎬 Luma Ray2 客户端测试")
    client = LumaRay2Client()
    
    # 测试文本到视频
    try:
        arn = client.text_to_video(
            prompt="A beautiful sunset over the ocean",
            s3_output_uri="s3://s3-demo-zy/luma_test/"
        )
        print(f"✅ 任务启动成功: {arn}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
