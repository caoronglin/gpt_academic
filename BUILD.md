# GPT Academic 构建指南

本文档介绍如何构建GPT Academic项目的Windows可执行文件和macOS应用程序安装包。

## 支持的模型

项目已配置支持以下模型：

### 语言模型 (LLM)
- **Qwen3-235B-A22B** (默认模型)
- **Qwen3-32B**
- **Qwen3-VL-235B-A22B-Instruct** (多模态模型)

### 嵌入模型 (Embedding)
- **BGE-M3** (默认嵌入模型)
- **BGE-Reranker-Large**
- **text-embedding-3-small**

## 构建要求

### 系统要求
- **Windows**: Windows 10/11, Python 3.8+
- **macOS**: macOS 10.15+, Python 3.8+
- **Linux**: Ubuntu 18.04+, Python 3.8+ (仅用于测试)

### 依赖要求
- Python 3.8+
- pip (最新版本)
- Git

## 本地构建

### 1. 安装依赖

```bash
# 克隆项目
git clone https://github.com/your-username/gpt-academic.git
cd gpt-academic

# 安装项目依赖
pip install -r requirements.txt

# 安装构建工具
pip install -r requirements-dev.txt
```

### 2. 配置模型API密钥

在 `config.py` 文件中配置相应的API密钥：

```python
# 阿里灵积云API密钥（用于Qwen3系列模型）
DASHSCOPE_API_KEY = "your-dashscope-api-key-here"

# 其他模型API密钥（根据需要配置）
# OPENAI_API_KEY = "your-openai-api-key"
# ...
```

### 3. 执行构建

使用提供的构建脚本：

```bash
# Windows
python build.py

# macOS
python3 build.py
```

构建完成后，可执行文件将生成在 `dist/` 目录中。

## GitHub Actions 自动化构建

项目配置了GitHub Actions工作流，支持以下功能：

### 触发条件
- **推送**到 `main` 或 `master` 分支
- **推送标签**（以 `v` 开头，如 `v1.0.0`）
- **拉取请求**

### 工作流任务

1. **测试阶段**
   - 在 Ubuntu、Windows、macOS 上运行
   - 测试 Python 3.8-3.11 兼容性
   - 验证模型配置和导入

2. **构建阶段**
   - **Windows**: 构建单文件可执行程序 (.exe)
   - **macOS**: 构建应用程序包 (.app)

3. **发布阶段**
   - 自动创建 GitHub Release
   - 上传构建产物
   - 生成发布说明

### 工作流文件位置

- `.github/workflows/build-and-release.yml`

## 构建产物

### Windows
- `GPT_Academic.exe` - 单文件可执行程序
- 包含所有依赖和资源文件

### macOS
- `GPT Academic.app` - 应用程序包
- 符合macOS应用规范
- 支持拖拽安装

## 配置说明

### 模型配置

在 `config.py` 中配置支持的模型：

```python
# 默认语言模型
LLM_MODEL = "dashscope-qwen3-235b-a22b"

# 可用语言模型列表
AVAIL_LLM_MODELS = [
    "dashscope-qwen3-235b-a22b",
    "dashscope-qwen3-32b", 
    "dashscope-qwen3-vl-235b-a22b-instruct",
    # ... 其他模型
]

# 默认嵌入模型
EMBEDDING_MODEL = "bge-m3"

# 可用嵌入模型列表
AVAIL_EMBEDDING_MODELS = ["bge-m3", "bge-reranker-large", "text-embedding-3-small"]
```

### 构建配置

构建脚本 `build.py` 自动处理以下配置：

- **隐藏导入**: 自动包含所有必要的Python模块
- **数据文件**: 包含配置文件、资源文件和模块目录
- **平台特定设置**: Windows和macOS的差异化配置

## 故障排除

### 常见问题

1. **构建失败：缺少依赖**
   ```bash
   # 重新安装依赖
   pip install --upgrade -r requirements.txt
   pip install --upgrade -r requirements-dev.txt
   ```

2. **运行时错误：模块未找到**
   - 检查 `build.py` 中的隐藏导入列表
   - 确保所有依赖模块都已正确打包

3. **macOS应用无法启动**
   - 检查应用包权限：`chmod +x "GPT Academic.app/Contents/MacOS/GPT_Academic"`
   - 验证Info.plist配置

4. **API密钥配置错误**
   - 确保在 `config.py` 中正确配置API密钥
   - 验证密钥权限和配额

### 调试构建

启用详细日志：
```bash
# Windows
python build.py --verbose

# macOS  
python3 build.py --verbose
```

检查构建日志：
- 查看 `build/` 目录中的临时文件
- 检查PyInstaller生成的警告和错误信息

## 版本管理

### 版本号规范
- 使用语义化版本号：`主版本.次版本.修订版本`
- 示例：`v1.2.3`

### 发布流程
1. 更新版本号
2. 创建Git标签：`git tag v1.2.3`
3. 推送标签：`git push origin v1.2.3`
4. GitHub Actions自动构建和发布

## 贡献指南

### 添加新模型
1. 在 `config.py` 中添加模型配置
2. 在 `request_llms/bridge_all.py` 中注册模型
3. 更新构建脚本中的隐藏导入
4. 测试构建和运行

### 修改构建配置
1. 更新 `build.py` 中的spec配置
2. 修改GitHub工作流文件
3. 测试多平台构建
4. 更新文档

## 许可证

本项目基于MIT许可证发布。详见 [LICENSE](LICENSE) 文件。

## 支持

如有问题或建议，请提交 [GitHub Issue](https://github.com/your-username/gpt-academic/issues)。