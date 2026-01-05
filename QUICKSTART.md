# 快速启动指南

## 项目已完成！

项目已经按照需求文档实现完成，包含以下功能：

✅ 用户注册和登录（JWT 认证）
✅ 数据集文件上传和管理
✅ 训练任务提交和管理
✅ 模型权重文件管理
✅ 模型对话功能

## 下一步操作

### 1. 配置后端环境

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 创建 .env 文件（从示例复制）
# Windows PowerShell:
Copy-Item .env.example .env

# 编辑 .env 文件，填入以下配置：
# - SSH_HOST: 远程服务器地址
# - SSH_USERNAME: SSH 用户名
# - SSH_PASSWORD: SSH 密码（或使用 SSH_KEY_PATH）
# - REMOTE_WORK_DIR: LlamaFactory 安装路径
# - SECRET_KEY: JWT 密钥（修改为随机字符串）
# - 其他配置项
```

### 2. 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端将在 http://localhost:8000 启动
API 文档：http://localhost:8000/docs

### 3. 配置前端环境

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:3000 启动

### 4. 测试流程

1. **注册账户**
   - 访问 http://localhost:3000/register
   - 创建新账户

2. **上传数据集**
   - 登录后进入"数据集"页面
   - 上传 JSON/JSONL 格式的数据集文件

3. **提交训练任务**
   - 进入"提交任务"页面
   - 填写任务信息并提交

4. **查看任务状态**
   - 在首页查看任务列表
   - 点击任务查看详情和日志

5. **使用模型对话**
   - 训练完成后，模型会自动添加到模型列表
   - 进入"对话"页面选择模型进行对话

## 注意事项

⚠️ **重要提示**：

1. **SSH 配置**：确保 `.env` 中的 SSH 配置正确，后端需要通过 SSH 连接到远程服务器

2. **远程服务器要求**：
   - 已安装 LlamaFactory
   - 可以 SSH 连接
   - 有足够的存储空间

3. **对话功能**：对话功能需要在远程服务器上部署 `chat_inference.py` 脚本
   - 脚本路径在 `.env` 的 `CHAT_SCRIPT_PATH` 中配置
   - 脚本内容参考需求文档 3.3.5 节

4. **数据库**：首次运行会自动创建 SQLite 数据库 `database.db`

5. **最小实现限制**：
   - 使用 SQLite（不适合生产环境）
   - 任务状态需要手动刷新
   - 对话响应可能较慢（每次建立 SSH 连接）

## 故障排除

### 后端启动失败
- 检查 Python 版本（需要 3.8+）
- 检查依赖是否安装完整
- 检查 `.env` 配置是否正确

### 前端启动失败
- 检查 Node.js 版本（需要 16+）
- 运行 `npm install` 重新安装依赖

### SSH 连接失败
- 检查 SSH 配置（主机、端口、用户名、密码/密钥）
- 测试 SSH 连接是否正常
- 检查防火墙设置

### 文件上传失败
- 检查远程服务器存储空间
- 检查 SSH 用户权限
- 检查远程目录路径是否正确

## 开发建议

这是最小实现版本，建议：

1. 先在测试环境验证功能
2. 根据实际需求调整配置
3. 生产环境使用前进行安全加固
4. 考虑使用 PostgreSQL 替代 SQLite
5. 添加更多错误处理和验证

祝使用愉快！🚀

