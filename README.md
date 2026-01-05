# 模型微调云服务平台

基于 LlamaFactory 的模型微调云服务平台，支持用户注册登录、数据集管理、任务提交、模型管理和对话功能。

## 项目结构

```
.
├── backend/          # 后端（FastAPI）
├── frontend/         # 前端（React + TypeScript + Vite）
└── 需求说明文档.md   # 详细的需求文档
```

## 快速开始

### 后端设置

1. 进入后端目录：
```bash
cd backend
```

2. 创建虚拟环境（推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
复制 `.env.example` 为 `.env` 并修改配置：
```bash
cp .env.example .env
# 编辑 .env 文件，填入 SSH 配置等信息
```

5. 启动服务：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端设置

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

前端将在 http://localhost:3000 运行。

## 功能特性

- ✅ 用户注册和登录（JWT 认证）
- ✅ 数据集文件上传和管理
- ✅ 训练任务提交和管理
- ✅ 模型权重文件管理
- ✅ 模型对话功能

## 注意事项

1. **SSH 配置**：需要正确配置 `.env` 文件中的 SSH 连接信息
2. **远程服务器**：需要确保远程服务器已安装 LlamaFactory
3. **对话脚本**：对话功能需要在远程服务器上部署 `chat_inference.py` 脚本（参考需求文档）
4. **数据库**：首次运行会自动创建 SQLite 数据库文件 `database.db`

## 开发说明

这是一个最小实现版本，主要用于演示核心功能。生产环境使用前需要：

- 使用 PostgreSQL 替代 SQLite
- 配置 HTTPS
- 加强安全性配置
- 优化错误处理
- 添加更多验证和错误处理

详细的需求说明请参考 `需求说明文档.md`。

