#!/bin/bash

# AWS Bedrock Luma Ray2 快速设置脚本

echo "🚀 AWS Bedrock Luma Ray2 视频生成工具 - 快速设置"
echo "=================================================="

# 检查Python环境
echo "1. 检查Python环境..."
if command -v python3 &> /dev/null; then
    echo "✅ Python3 已安装: $(python3 --version)"
else
    echo "❌ 请先安装Python3"
    exit 1
fi

# 检查pip
if command -v pip3 &> /dev/null; then
    echo "✅ pip3 已安装"
else
    echo "❌ 请先安装pip3"
    exit 1
fi

# 安装依赖
echo ""
echo "2. 安装Python依赖..."
pip3 install -r requirements.txt

# 检查AWS CLI
echo ""
echo "3. 检查AWS CLI..."
if command -v aws &> /dev/null; then
    echo "✅ AWS CLI 已安装: $(aws --version)"
    
    # 检查AWS凭证
    if aws sts get-caller-identity &> /dev/null; then
        echo "✅ AWS凭证配置正确"
        aws sts get-caller-identity
    else
        echo "⚠️  AWS凭证未配置，请运行: aws configure"
    fi
else
    echo "⚠️  AWS CLI 未安装，请先安装AWS CLI"
fi

# 检查S3桶
echo ""
echo "4. 检查S3桶..."
BUCKET_NAME="s3-demo-zy"
if aws s3 ls "s3://$BUCKET_NAME" &> /dev/null; then
    echo "✅ S3桶 $BUCKET_NAME 存在"
else
    echo "⚠️  S3桶 $BUCKET_NAME 不存在"
    read -p "是否创建S3桶? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        aws s3 mb "s3://$BUCKET_NAME" --region us-west-2
        echo "✅ S3桶创建成功"
        
        # 设置桶策略
        echo "设置桶策略..."
        cat > bucket-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock.amazonaws.com"
      },
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::$BUCKET_NAME/luma_test/*"
    }
  ]
}
EOF
        aws s3api put-bucket-policy --bucket "$BUCKET_NAME" --policy file://bucket-policy.json
        rm bucket-policy.json
        echo "✅ 桶策略设置完成"
    fi
fi

# 运行测试
echo ""
echo "5. 运行快速测试..."
python3 -c "
from luma_ray2_client import LumaRay2Client
try:
    client = LumaRay2Client()
    print('✅ 客户端初始化成功')
    
    # 测试列出任务
    jobs = client.list_jobs(max_results=1)
    print('✅ API连接正常')
except Exception as e:
    print(f'❌ 测试失败: {e}')
"

echo ""
echo "🎉 设置完成！"
echo ""
echo "📚 使用方法:"
echo "  python3 examples.py  # 运行示例"
echo ""
echo "📖 更多信息请查看 README.md"
