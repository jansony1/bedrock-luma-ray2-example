#!/usr/bin/env python3
"""
AWS Bedrock Luma Ray2 使用示例
演示各种视频生成场景
"""

from luma_ray2_client import LumaRay2Client
import logging
from pathlib import Path

# 设置日志级别
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """主函数示例"""
    # 初始化客户端
    client = LumaRay2Client(region_name='us-west-2')
    
    # 配置S3输出路径
    s3_output_uri = "s3://s3-demo-zy/luma_test/"
    
    try:
        # 示例1: 文本到视频
        print("\n" + "="*50)
        print("示例1: 文本到视频生成")
        print("="*50)
        text_prompt = "一只橙色的小猫在绿色的草地上追逐蝴蝶，阳光透过树叶洒下斑驳的光影"
        
        invocation_arn = client.text_to_video(
            prompt=text_prompt,
            s3_output_uri=s3_output_uri,
            aspect_ratio="16:9",
            duration="5s",
            resolution="720p",
            loop=False
        )
        
        print(f"\n📋 任务已启动，ARN: {invocation_arn}")
        
        # 等待完成
        print("\n⏳ 等待任务完成...")
        result = client.wait_for_completion(invocation_arn, max_wait_time=600)
        
        if result and result['status'] == 'Completed':
            print("✅ 视频生成成功！")
        elif result and result['status'] == 'Failed':
            print("❌ 视频生成失败")
        else:
            print("⏰ 任务超时")
        
        # 示例2: 本地图片到视频
        local_image_path = "input_image.jpg"
        if Path(local_image_path).exists():
            print("\n" + "="*50)
            print("示例2: 本地图片到视频生成")
            print("="*50)
            image_prompt = "让图片中的场景动起来，添加微风吹动的效果，树叶轻摆"
            
            invocation_arn = client.image_to_video(
                prompt=image_prompt,
                s3_output_uri=s3_output_uri,
                start_image_path=local_image_path,
                aspect_ratio="16:9",
                duration="5s",
                resolution="720p"
            )
            
            print(f"\n📋 本地图片到视频任务已启动，ARN: {invocation_arn}")
        else:
            print(f"\n⚠️  本地图片文件不存在: {local_image_path}")
        
        # 示例3: S3图片到视频
        print("\n" + "="*50)
        print("示例3: S3图片到视频生成")
        print("="*50)
        s3_image_path = "s3://s3-demo-zy/images/sample.jpg"  # 示例S3路径
        s3_image_prompt = "让这张图片中的水面波光粼粼，云朵缓缓移动"
        
        try:
            invocation_arn = client.image_to_video(
                prompt=s3_image_prompt,
                s3_output_uri=s3_output_uri,
                start_image_path=s3_image_path,
                aspect_ratio="16:9",
                duration="5s",
                resolution="720p"
            )
            
            print(f"\n📋 S3图片到视频任务已启动，ARN: {invocation_arn}")
            
        except Exception as e:
            print(f"⚠️  S3图片处理失败（可能图片不存在）: {str(e)}")
        
        # 示例4: 双关键帧图片到视频（起始帧+结束帧）
        print("\n" + "="*50)
        print("示例4: 双关键帧图片到视频生成")
        print("="*50)
        
        # 可以混合使用本地和S3路径
        start_image = "input_start.jpg"  # 本地文件
        end_image = "s3://s3-demo-zy/images/end_frame.jpg"  # S3文件
        transition_prompt = "从起始场景平滑过渡到结束场景，添加自然的动画效果"
        
        # 检查起始图片是否存在
        if Path(start_image).exists():
            try:
                invocation_arn = client.image_to_video(
                    prompt=transition_prompt,
                    s3_output_uri=s3_output_uri,
                    start_image_path=start_image,
                    end_image_path=end_image,
                    aspect_ratio="16:9",
                    duration="9s",  # 使用9秒时长
                    resolution="720p"
                )
                
                print(f"\n📋 双关键帧任务已启动，ARN: {invocation_arn}")
                
            except Exception as e:
                print(f"⚠️  双关键帧处理失败: {str(e)}")
        else:
            print(f"⚠️  起始图片文件不存在: {start_image}")
        
        # 示例5: 列出所有任务
        print("\n" + "="*50)
        print("当前任务列表")
        print("="*50)
        try:
            jobs = client.list_jobs(max_results=5)
            for i, job in enumerate(jobs.get('asyncInvokes', []), 1):
                status_emoji = {
                    'Completed': '✅',
                    'Failed': '❌',
                    'InProgress': '⏳',
                    'Submitted': '📤'
                }.get(job['status'], '❓')
                
                print(f"{i}. {status_emoji} 状态: {job['status']}")
                print(f"   ARN: {job['invocationArn']}")
                if 'submitTime' in job:
                    print(f"   提交时间: {job['submitTime']}")
                print()
        except Exception as e:
            logger.error(f"获取任务列表失败: {str(e)}")
    
    except Exception as e:
        logger.error(f"执行过程中出错: {str(e)}")


def simple_examples():
    """简单使用示例"""
    print("🎬 Luma Ray2 视频生成示例")
    print("=" * 50)
    
    # 初始化客户端
    client = LumaRay2Client()
    
    # 输出S3路径
    output_path = "s3://s3-demo-zy/luma_test/"
    
    # 1. 纯文本生成视频
    print("\n1️⃣ 文本到视频")
    text_prompt = "一只可爱的金毛犬在海滩上奔跑，夕阳西下，海浪轻拍沙滩"
    
    try:
        arn = client.text_to_video(
            prompt=text_prompt,
            s3_output_uri=output_path,
            duration="5s",
            resolution="720p"
        )
        print(f"✅ 任务启动成功: {arn}")
    except Exception as e:
        print(f"❌ 任务启动失败: {e}")
    
    # 2. 本地图片生成视频
    print("\n2️⃣ 本地图片到视频")
    local_image = "./my_photo.jpg"  # 替换为您的本地图片路径
    image_prompt = "让这张照片中的场景充满生机，添加自然的动态效果"
    
    try:
        arn = client.image_to_video(
            prompt=image_prompt,
            s3_output_uri=output_path,
            start_image_path=local_image,  # 本地文件路径
            duration="5s"
        )
        print(f"✅ 本地图片任务启动成功: {arn}")
    except Exception as e:
        print(f"❌ 本地图片任务失败: {e}")
    
    # 3. S3图片生成视频
    print("\n3️⃣ S3图片到视频")
    s3_image = "s3://s3-demo-zy/input-images/landscape.jpg"  # 替换为您的S3图片路径
    s3_prompt = "让这个风景画面动起来，云朵飘动，树叶摇摆"
    
    try:
        arn = client.image_to_video(
            prompt=s3_prompt,
            s3_output_uri=output_path,
            start_image_path=s3_image,  # S3路径
            duration="5s"
        )
        print(f"✅ S3图片任务启动成功: {arn}")
    except Exception as e:
        print(f"❌ S3图片任务失败: {e}")
    
    # 4. 检查任务状态
    print("\n4️⃣ 检查最近的任务状态")
    try:
        jobs = client.list_jobs(max_results=3)
        for i, job in enumerate(jobs.get('asyncInvokes', []), 1):
            status = job['status']
            status_emoji = {
                'Completed': '✅',
                'Failed': '❌', 
                'InProgress': '⏳',
                'Submitted': '📤'
            }.get(status, '❓')
            
            print(f"{i}. {status_emoji} {status}")
            print(f"   ARN: {job['invocationArn']}")
    except Exception as e:
        print(f"❌ 获取任务列表失败: {e}")


if __name__ == "__main__":
    # 运行完整示例
    main()
    
    # 或者运行简单示例
    # simple_examples()
