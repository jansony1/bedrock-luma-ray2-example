#!/usr/bin/env python3
"""
生成奥特曼大战哥斯拉视频 - 使用正确的boto3方法
"""

from luma_ray2_client_complete import LumaRay2Client
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("🎬 奥特曼大战哥斯拉 - 使用正确的boto3方法")
    print("=" * 60)
    
    # 使用boto3标准方法（已修正）
    client = LumaRay2Client(use_raw_http=False)
    
    # 输出S3路径
    s3_output_uri = "s3://s3-demo-zy/luma_test/"
    
    # 奥特曼大战哥斯拉的详细prompt
    prompt = "Ultraman and Godzilla engaged in an epic battle in the deep blue ocean, massive water splashes erupting around them, Ultraman firing brilliant light beams from his hands, Godzilla breathing atomic fire, towering waves crashing, dramatic underwater combat scene, cinematic lighting, spectacular action sequence"
    
    try:
        print(f"🎯 视频内容: 奥特曼和哥斯拉在深蓝色海洋中的史诗级战斗")
        print(f"🔧 调用方法: boto3标准方法（已修正）")
        print(f"📍 输出位置: {s3_output_uri}")
        print(f"⏱️  视频时长: 5秒")
        print(f"📺 分辨率: 720p")
        print(f"📐 宽高比: 16:9")
        print()
        
        # 调用修正版的boto3方法
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
        print("🎬 正在生成奥特曼发射光线攻击哥斯拉的精彩场面...")
        
        # 等待任务完成
        result = client.wait_for_completion(invocation_arn, max_wait_time=600)
        
        if result and result['status'] == 'Completed':
            print("\n🎉 视频生成成功！")
            print("🎬 您的奥特曼大战哥斯拉海战视频已经生成完成！")
            
            # 获取输出信息
            output_config = result.get('outputDataConfig', {})
            s3_output = output_config.get('s3OutputDataConfig', {})
            output_uri = s3_output.get('s3Uri', '')
            
            if output_uri:
                print(f"📁 视频保存位置: {output_uri}")
                print(f"💾 您可以在S3控制台或使用AWS CLI下载视频文件")
                print(f"📥 下载命令: aws s3 cp {output_uri} ./ultraman_vs_godzilla_boto3.mp4 --recursive")
            
            print(f"\n📊 任务详情:")
            print(f"   - 状态: {result['status']}")
            print(f"   - 调用方法: boto3标准方法 ✅")
            print(f"   - 提交时间: {result.get('submitTime', 'N/A')}")
            if 'endTime' in result:
                print(f"   - 完成时间: {result['endTime']}")
            
            print(f"\n🎊 恭喜！您的奥特曼vs哥斯拉海战视频制作完成！")
            print(f"🌊 视频包含了激烈的海战场面、光线攻击和原子吐息等精彩内容")
            print(f"🔧 使用了修正后的boto3标准方法，无需原始HTTP请求！")
            
        elif result and result['status'] == 'Failed':
            print("\n❌ 视频生成失败")
            error_msg = result.get('failureMessage', '未知错误')
            print(f"🚨 错误信息: {error_msg}")
            
        else:
            print("\n⏰ 任务超时")
            print("💡 您可以稍后使用以下命令检查任务状态:")
            print(f"   python3 -c \"from luma_ray2_client_complete import LumaRay2Client; client = LumaRay2Client(); print(client.get_job_status('{invocation_arn}'))\"")
    
    except Exception as e:
        print(f"\n❌ 程序执行出错: {str(e)}")
        logger.error(f"执行过程中出错: {str(e)}")

if __name__ == "__main__":
    main()
