#!/usr/bin/env python3
"""
生成奥特曼大战哥斯拉视频
"""

from luma_ray2_client import LumaRay2Client
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("🎬 开始生成奥特曼大战哥斯拉视频")
    print("=" * 50)
    
    # 初始化客户端
    client = LumaRay2Client(region_name='us-west-2')
    
    # 输出S3路径
    s3_output_uri = "s3://s3-demo-zy/luma_test/"
    
    # 奥特曼大战哥斯拉的prompt
    prompt = "奥特曼和哥斯拉在深蓝色的海洋中激烈战斗，巨大的水花四溅，奥特曼发出光线攻击，哥斯拉喷射原子吐息，海浪翻滚，场面震撼壮观"
    
    try:
        print(f"🎯 生成视频内容: {prompt}")
        print(f"📍 输出位置: {s3_output_uri}")
        print(f"⏱️  视频时长: 5秒")
        print(f"📺 分辨率: 720p")
        print(f"📐 宽高比: 16:9")
        print()
        
        # 调用文本到视频生成
        invocation_arn = client.text_to_video(
            prompt=prompt,
            s3_output_uri=s3_output_uri,
            aspect_ratio="16:9",
            duration="5s",
            resolution="720p",
            loop=False
        )
        
        print(f"\n✅ 视频生成任务已启动！")
        print(f"📋 任务ARN: {invocation_arn}")
        print(f"\n⏳ 正在等待视频生成完成...")
        print("💡 提示: 5秒视频通常需要2-5分钟生成时间")
        
        # 等待任务完成
        result = client.wait_for_completion(invocation_arn, max_wait_time=600)
        
        if result and result['status'] == 'Completed':
            print("\n🎉 视频生成成功！")
            print("🎬 您的奥特曼大战哥斯拉视频已经生成完成")
            
            # 获取输出信息
            output_config = result.get('outputDataConfig', {})
            s3_output = output_config.get('s3OutputDataConfig', {})
            output_uri = s3_output.get('s3Uri', '')
            
            if output_uri:
                print(f"📁 视频保存位置: {output_uri}")
                print(f"💾 您可以在S3控制台查看生成的视频文件")
            
            print(f"\n📊 任务详情:")
            print(f"   - 状态: {result['status']}")
            print(f"   - 提交时间: {result.get('submitTime', 'N/A')}")
            if 'endTime' in result:
                print(f"   - 完成时间: {result['endTime']}")
            
        elif result and result['status'] == 'Failed':
            print("\n❌ 视频生成失败")
            error_msg = result.get('failureMessage', '未知错误')
            print(f"🚨 错误信息: {error_msg}")
            
        else:
            print("\n⏰ 任务超时")
            print("💡 您可以稍后使用以下命令检查任务状态:")
            print(f"   python3 -c \"from luma_ray2_client import LumaRay2Client; client = LumaRay2Client(); print(client.get_job_status('{invocation_arn}'))\"")
    
    except Exception as e:
        print(f"\n❌ 程序执行出错: {str(e)}")
        logger.error(f"执行过程中出错: {str(e)}")

if __name__ == "__main__":
    main()
