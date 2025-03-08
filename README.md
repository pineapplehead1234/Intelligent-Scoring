# 语音相似度评分系统安装指南

## 环境要求

- Python 3.8 或更高版本
- CUDA支持（可选，用于GPU加速）

## 安装步骤

### 1. 克隆项目

首先，将项目克隆到本地：

```bash
git clone https://github.com/pineapplehead1234/Intelligent-Scoring
cd teststt
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv venv

# Windows激活虚拟环境
venv\Scripts\activate

# Linux/Mac激活虚拟环境
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖包括：

- Flask 3.0.2 - Web应用框架
- Flask-CORS 4.0.0 - 处理跨域请求
- Transformers 4.38.2 - Hugging Face转换器库
- Sentence-Transformers 2.5.1 - 文本相似度计算
- PyTorch 2.2.1 - 深度学习框架
- Werkzeug 3.0.1 - WSGI工具库

### 4. 环境变量配置

项目使用了以下环境变量，已在代码中设置：

- HF_ENDPOINT="<https://hf-mirror.com>" - Hugging Face模型镜像
- CUDA_VISIBLE_DEVICES="0" - GPU设备选择
- TF_ENABLE_ONEDNN_OPTS="0" - TensorFlow优化选项

### 5. 运行应用

```bash
# 进入后端目录
cd backend

# 启动Flask应用
python api.py
```

应用将在 <http://localhost:5000> 启动

## 注意事项

1. 首次运行时会自动下载所需的模型文件，请确保网络连接正常
2. 如果遇到模型下载速度慢的问题，项目已配置使用镜像地址
3. 确保系统有足够的存储空间用于存放模型文件
4. 如果使用GPU加速，请确保已正确安装CUDA和对应版本的PyTorch

## 常见问题

1. 如果安装依赖时出现错误，可以尝试更新pip：

```bash
python -m pip install --upgrade pip
```

2. 如果模型下载失败，可以手动下载模型文件并放置在正确的缓存目录中

3. 如果遇到CUDA相关错误，请确认PyTorch版本与本地CUDA版本匹配

## 技术支持

如果在安装过程中遇到问题，请查看项目的issue页面或提交新的issue。
