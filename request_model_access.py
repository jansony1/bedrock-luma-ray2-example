#!/usr/bin/env python3
"""
AWS Bedrock 模型访问权限申请指南
"""

import boto3
import json

def check_model_access():
    print("🔍 检查AWS Bedrock模型访问权限")
    print("=" * 60)
    
    bedrock = boto3.client('bedrock', region_name='us-west-2')
    bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')
    
    # 1. 列出所有可用模型
    print("📋 可用的基础模型:")
    try:
        models = bedrock.list_foundation_models()
        for model in models['modelSummaries']:
            if 'luma' in model['modelId'].lower():
                print(f"   🎬 {model['modelId']} - {model['modelName']} ({model['providerName']})")
                print(f"      状态: {model['modelLifecycle']['status']}")
                print(f"      输入: {', '.join(model['inputModalities'])}")
                print(f"      输出: {', '.join(model['outputModalities'])}")
    except Exception as e:
        print(f"❌ 获取模型列表失败: {e}")
        return
    
    # 2. 测试Luma模型访问
    print(f"\n🧪 测试Luma Ray2模型访问权限:")
    try:
        response = bedrock_runtime.start_async_invoke(
            modelId="luma.ray-v2:0",
            modelInput='{"prompt": "test"}',
            outputDataConfig={
                "s3OutputDataConfig": {
                    "s3Uri": "s3://s3-demo-zy/luma_test/"
                }
            }
        )
        print(f"✅ Luma Ray2模型访问正常!")
        print(f"   任务ARN: {response['invocationArn']}")
        return True
    except Exception as e:
        error_str = str(e)
        print(f"❌ Luma Ray2模型访问失败: {e}")
        
        if "AccessDenied" in error_str or "don't have access" in error_str:
            print(f"\n💡 需要申请模型访问权限!")
            print_access_instructions()
        elif "ValidationException" in error_str:
            print(f"\n💡 模型可访问，但请求格式有问题")
        
        return False

def print_access_instructions():
    print(f"\n📝 申请AWS Bedrock模型访问权限的步骤:")
    print(f"=" * 60)
    print(f"1. 🌐 打开AWS控制台: https://console.aws.amazon.com/")
    print(f"2. 🔍 搜索并进入 'Amazon Bedrock' 服务")
    print(f"3. 📍 确保区域选择为: us-west-2 (Oregon)")
    print(f"4. 📋 在左侧菜单中点击 'Model access'")
    print(f"5. 🔓 点击 'Request model access' 或 'Manage model access'")
    print(f"6. 🎬 找到 'Luma AI' 提供商")
    print(f"7. ✅ 勾选 'Ray v2' 模型")
    print(f"8. 📝 填写使用案例说明 (例如: 'Video generation for creative projects')")
    print(f"9. 📤 提交申请")
    print(f"10. ⏳ 等待审批 (通常几分钟到几小时)")
    
    print(f"\n⚠️  注意事项:")
    print(f"   • 某些模型可能需要额外的审批流程")
    print(f"   • 确保您的AWS账户有足够的权限申请模型访问")
    print(f"   • 申请时需要提供合理的使用案例说明")
    
    print(f"\n🔄 申请完成后，请重新运行此脚本验证访问权限")

def main():
    print("🎬 AWS Bedrock Luma Ray2 模型访问检查")
    print("=" * 60)
    
    # 检查基本AWS权限
    try:
        sts = boto3.client('sts', region_name='us-west-2')
        identity = sts.get_caller_identity()
        print(f"✅ AWS身份: {identity.get('Arn', 'N/A')}")
        print(f"✅ 账户ID: {identity.get('Account', 'N/A')}")
    except Exception as e:
        print(f"❌ AWS身份验证失败: {e}")
        return
    
    # 检查模型访问
    has_access = check_model_access()
    
    if has_access:
        print(f"\n🎉 恭喜! 您已经有Luma Ray2模型的访问权限")
        print(f"🚀 现在可以运行视频生成程序了:")
        print(f"   python3 generate_ultraman_vs_godzilla.py")
    else:
        print(f"\n📋 请按照上述步骤申请模型访问权限")
        print(f"🔄 申请完成后，重新运行: python3 request_model_access.py")

if __name__ == "__main__":
    main()
