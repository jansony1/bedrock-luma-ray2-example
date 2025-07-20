# AWS Bedrock Luma Ray2 问题解决方案

## 🚨 当前问题

您的代码和环境配置都是正确的，但是在调用Luma Ray2模型时遇到了 `ValidationException: The provided request is not valid` 错误。

## 🔍 问题分析

经过详细调试，发现：

1. ✅ **AWS凭证正常**: 身份验证成功
2. ✅ **S3权限正常**: 可以读写S3桶
3. ✅ **Bedrock基本权限正常**: 可以列出模型
4. ✅ **Bedrock Runtime权限正常**: 可以调用异步API
5. ✅ **模型存在且活跃**: Luma Ray2模型状态为ACTIVE
6. ✅ **API格式正确**: 按照官方文档格式调用
7. ✅ **boto3版本正确**: 1.39.9支持异步API

## 💡 根本原因

**需要在AWS Bedrock控制台中申请Luma Ray2模型的访问权限！**

虽然模型显示为ACTIVE状态，但这只是表示模型在AWS中可用，您的账户还需要单独申请访问权限。

## 🛠️ 解决步骤

### 步骤1: 申请模型访问权限

1. **打开AWS控制台**: https://console.aws.amazon.com/
2. **进入Bedrock服务**: 搜索 "Amazon Bedrock"
3. **选择正确区域**: 确保选择 `us-west-2` (Oregon)
4. **申请模型访问**:
   - 点击左侧菜单 "Model access"
   - 点击 "Request model access" 或 "Manage model access"
   - 找到 "Luma AI" 提供商
   - 勾选 "Ray v2" 模型
   - 填写使用案例: "Video generation for creative and educational projects"
   - 提交申请

### 步骤2: 等待审批

- 通常几分钟到几小时内会获得批准
- 您会收到邮件通知

### 步骤3: 验证访问权限

申请批准后，运行验证脚本：

```bash
cd /Users/zhenyin/aws-bedrock-luma-ray2
source venv/bin/activate
python3 request_model_access.py
```

### 步骤4: 生成奥特曼vs哥斯拉视频

权限获得后，运行视频生成：

```bash
python3 generate_ultraman_vs_godzilla.py
```

## 📋 预期结果

权限获得后，您应该看到：

```
🎬 开始生成奥特曼大战哥斯拉视频
==================================================
🎯 生成视频内容: 奥特曼和哥斯拉在深蓝色的海洋中激烈战斗...
📍 输出位置: s3://s3-demo-zy/luma_test/
⏱️  视频时长: 5秒
📺 分辨率: 720p
📐 宽高比: 16:9

=== 启动文本到视频生成任务 ===
Prompt: 奥特曼和哥斯拉在深蓝色的海洋中激烈战斗...
参数配置:
  - 宽高比: 16:9
  - 时长: 5s
  - 分辨率: 720p
  - 循环播放: False
  - 输出路径: s3://s3-demo-zy/luma_test/
✅ 文本到视频任务已启动: arn:aws:bedrock:us-west-2:269562551342:async-invoke/xxxxx

⏳ 正在等待视频生成完成...
💡 提示: 5秒视频通常需要2-5分钟生成时间
```

## ⚠️ 注意事项

1. **费用**: Luma Ray2按视频时长计费，5秒视频大约$0.50-1.00
2. **处理时间**: 5秒视频需要2-5分钟，9秒视频需要4-8分钟
3. **区域限制**: 目前只在us-west-2区域可用
4. **配额限制**: 新账户可能有并发任务限制

## 🎯 最终目标

成功生成5秒钟的奥特曼大战哥斯拉海战视频，保存在S3桶中！

## 📞 需要帮助？

如果申请权限后仍有问题，请运行诊断脚本：

```bash
python3 debug_api_call.py
```

或联系AWS支持获取帮助。
