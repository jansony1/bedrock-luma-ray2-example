# GitHub 上传指南

## 🚀 快速上传到GitHub

### 方法1: 使用GitHub CLI (推荐)

1. **安装GitHub CLI**
   ```bash
   # macOS
   brew install gh
   
   # 或下载安装包
   # https://cli.github.com/
   ```

2. **登录GitHub**
   ```bash
   gh auth login
   ```

3. **创建仓库并上传**
   ```bash
   cd /Users/zhenyin/aws-bedrock-luma-ray2
   gh repo create aws-bedrock-luma-ray2 --public --source=. --remote=origin --push
   ```

### 方法2: 使用Git命令

1. **在GitHub网站创建新仓库**
   - 访问 https://github.com/new
   - 仓库名: `aws-bedrock-luma-ray2`
   - 设置为Public
   - 不要初始化README (我们已经有了)

2. **添加远程仓库并推送**
   ```bash
   cd /Users/zhenyin/aws-bedrock-luma-ray2
   git remote add origin https://github.com/YOUR_USERNAME/aws-bedrock-luma-ray2.git
   git branch -M main
   git push -u origin main
   ```

### 方法3: 使用GitHub Desktop

1. **下载GitHub Desktop**
   - https://desktop.github.com/

2. **发布仓库**
   - 打开GitHub Desktop
   - File → Add Local Repository
   - 选择 `/Users/zhenyin/aws-bedrock-luma-ray2`
   - 点击 "Publish repository"

## 📋 仓库信息

- **仓库名**: `aws-bedrock-luma-ray2`
- **描述**: AWS Bedrock Luma Ray2 video generation tool with support for text-to-video and image-to-video generation
- **标签**: `aws`, `bedrock`, `luma`, `video-generation`, `python`, `ai`, `machine-learning`

## 🔧 上传后的设置

### 1. 设置仓库描述和标签
在GitHub仓库页面点击设置图标，添加：
- **Description**: AWS Bedrock Luma Ray2 video generation tool
- **Topics**: aws, bedrock, luma, video-generation, python, ai, machine-learning

### 2. 创建Release
```bash
# 创建标签
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0

# 或使用GitHub CLI
gh release create v1.0.0 --title "v1.0.0 - Initial Release" --notes "First stable release of AWS Bedrock Luma Ray2 video generation tool"
```

### 3. 设置GitHub Pages (可选)
如果想要文档网站：
- Settings → Pages
- Source: Deploy from a branch
- Branch: main / docs

## 📁 最终项目结构

```
aws-bedrock-luma-ray2/
├── luma_ray2_client.py    # 主要客户端类
├── examples.py            # 使用示例
├── requirements.txt       # 依赖包
├── setup.sh              # 快速安装脚本
├── README.md             # 项目说明
├── .gitignore           # Git忽略文件
├── LICENSE              # MIT许可证
└── GITHUB_UPLOAD.md     # 上传指南
```

## 🎯 推荐的GitHub仓库设置

### README徽章
在README.md顶部添加：
```markdown
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![AWS](https://img.shields.io/badge/AWS-Bedrock-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
```

### 贡献指南
创建 `CONTRIBUTING.md` 文件说明如何贡献代码。

### 问题模板
在 `.github/ISSUE_TEMPLATE/` 创建问题模板。

## 🔗 有用的链接

- [GitHub CLI文档](https://cli.github.com/manual/)
- [Git基础教程](https://git-scm.com/book)
- [GitHub Desktop](https://desktop.github.com/)
- [Markdown语法](https://guides.github.com/features/mastering-markdown/)
