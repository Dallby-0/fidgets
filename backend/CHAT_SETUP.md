# Chat功能设置说明

## 概述

Chat功能支持两种模式：
1. **CLI模式**（默认）：使用交互式的 `llamafactory-cli chat` 命令
2. **Script模式**：使用Python脚本调用LlamaFactory API

## CLI模式设置（当前推荐）

### 1. 安装pexpect（远程服务器）

在远程服务器上安装pexpect：

```bash
pip install pexpect
```

### 2. 部署包装脚本

将 `chat_cli_wrapper.py` 上传到远程服务器，例如：

```bash
# 在本地执行（从backend目录）
scp backend/chat_cli_wrapper.py user@remote-server:/path/to/llamafactory/chat_cli_wrapper.py

# 在远程服务器上设置执行权限
ssh user@remote-server "chmod +x /path/to/llamafactory/chat_cli_wrapper.py"
```

### 3. 配置环境变量

在后端项目的 `.env` 文件中配置：

```env
# 使用CLI模式
CHAT_MODE=cli

# 包装脚本路径（远程服务器上的路径，绝对路径或相对于remote_work_dir的相对路径）
CHAT_SCRIPT_PATH=/path/to/llamafactory/chat_cli_wrapper.py
# 或者使用相对路径（相对于remote_work_dir）：
# CHAT_SCRIPT_PATH=chat_cli_wrapper.py

# 工作目录（LlamaFactory安装路径，脚本会在此目录下执行）
REMOTE_WORK_DIR=/root/LLaMA-Factory

# Conda环境名称（如果llamafactory-cli在conda环境中，需要设置）
# 如果不需要conda环境，可以不设置或留空
CONDA_ENV=base

# LlamaFactory CLI路径（如果在PATH中，可以不设置）
LLAMAFACTORY_CLI_PATH=llamafactory-cli

# 对话超时时间（秒）
CHAT_TIMEOUT=300
```

**重要提示**：
- `REMOTE_WORK_DIR` 应该设置为 `llamafactory-cli` 所在的目录（通常是 LLaMA-Factory 的安装目录）
- 脚本会在 `REMOTE_WORK_DIR` 目录下执行，确保脚本路径正确
- 如果 `llamafactory-cli` 在 conda 环境中，设置 `CONDA_ENV` 会自动激活该环境

### 4. 测试脚本

在远程服务器上测试脚本是否正常工作：

```bash
python3 /path/to/llamafactory/chat_cli_wrapper.py '{
  "base_model_path": "/root/autodl-tmp/Qwen2-0.5B-Instruct",
  "adapter_path": "/root/autodl-tmp/out",
  "template": "qwen2",
  "message": "你好"
}'
```

应该返回JSON格式的响应：
```json
{"role": "assistant", "content": "你好！有什么可以帮助你的吗？"}
```

## Script模式设置（备选方案）

如果你有一个使用LlamaFactory Python API的脚本，可以使用Script模式：

### 1. 准备Python脚本

在远程服务器上创建 `chat_inference.py`（参考需求文档中的示例）：

```python
#!/usr/bin/env python3
import sys
import json
from llamafactory import ChatModel

def main():
    config = json.loads(sys.argv[1])
    # ... 实现推理逻辑 ...
    result = {"role": "assistant", "content": "..."}
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
```

### 2. 配置环境变量

```env
# 使用Script模式
CHAT_MODE=script

# Python脚本路径
CHAT_SCRIPT_PATH=/path/to/llamafactory/chat_inference.py

# 对话超时时间
CHAT_TIMEOUT=300
```

## 工作原理

### CLI模式工作流程：

1. 后端接收对话请求
2. 构建配置JSON（包含模型路径、adapter路径、模板和用户消息）
3. 通过SSH执行远程包装脚本 `chat_cli_wrapper.py`
4. 包装脚本使用pexpect：
   - 启动 `llamafactory-cli chat` 命令
   - 等待欢迎消息和提示符
   - 发送用户消息
   - 等待并提取Assistant回复
   - 返回JSON格式结果
5. 后端解析JSON并返回给前端

### 注意事项：

1. **性能考虑**：每次对话都会重新加载模型，第一次调用会比较慢（模型加载时间）
2. **超时设置**：根据模型大小和硬件配置调整 `CHAT_TIMEOUT`
3. **错误处理**：如果pexpect超时或无法提取回复，会返回错误信息
4. **日志输出**：包装脚本的日志输出到stderr，不影响JSON结果

## 故障排查

### 问题1：pexpect超时

**原因**：模型加载时间过长或命令执行时间超过超时限制

**解决**：
- 增加超时时间（在`.env`中设置`CHAT_TIMEOUT`）
- 检查远程服务器性能

### 问题2：无法提取Assistant回复

**原因**：`llamafactory-cli chat`的输出格式与预期不符

**解决**：
- 查看远程服务器上的实际输出格式
- 调整`chat_cli_wrapper.py`中的正则表达式模式

### 问题3：命令找不到（llamafactory-cli: command not found）

**原因**：`llamafactory-cli`不在PATH中，或SSH执行时环境变量未加载

**解决**：
1. 检查在远程服务器上直接执行是否能找到命令：
   ```bash
   which llamafactory-cli
   ```
2. 如果命令在conda环境中，设置`.env`中的`CONDA_ENV`
3. 确保`REMOTE_WORK_DIR`设置为正确的目录
4. 如果仍不行，在`chat_cli_wrapper.py`中使用绝对路径

### 问题4：工作路径问题（最常见）

**症状**：在远程服务器上直接运行可以，但通过SSH执行失败

**原因**：SSH执行时工作目录或环境变量不正确

**解决**：
1. **检查脚本路径**：确保`CHAT_SCRIPT_PATH`使用绝对路径，或确保相对路径相对于`REMOTE_WORK_DIR`正确
2. **检查工作目录**：确保`REMOTE_WORK_DIR`设置为`llamafactory-cli`所在的目录
3. **检查conda环境**：如果使用conda，设置`CONDA_ENV`
4. **测试命令**：在远程服务器上测试完整命令：
   ```bash
   cd /root/LLaMA-Factory && python3 chat_cli_wrapper.py '{"base_model_path": "...", "adapter_path": "...", "template": "qwen2", "message": "你好"}'
   ```

### 问题5：Python路径问题

**原因**：SSH执行时使用的python3与本地不同

**解决**：
- 在远程服务器上确认python3路径：`which python3`
- 如果需要特定python，修改命令或使用虚拟环境

## 性能优化建议

1. **模型服务化**：对于频繁调用的场景，考虑部署一个长期运行的模型服务（不在最小实现范围内）
2. **连接复用**：可以考虑SSH连接复用（当前实现每次新建连接）
3. **异步执行**：前端可以使用异步请求，避免阻塞UI

