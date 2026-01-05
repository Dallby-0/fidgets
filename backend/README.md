# 后端服务

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量：
复制 `.env.example` 为 `.env` 并修改：
```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下内容：
- SSH 连接信息（远程服务器）
- SECRET_KEY（JWT Token 密钥）
- 其他配置项

3. 启动服务：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务将在 http://localhost:8000 运行。

API 文档：http://localhost:8000/docs

## 注意事项

- 首次运行会自动创建 SQLite 数据库
- 确保远程服务器已安装 LlamaFactory
- 对话功能需要在远程服务器上部署 `chat_inference.py` 脚本

