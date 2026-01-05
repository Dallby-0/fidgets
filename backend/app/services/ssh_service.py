import paramiko
import json
import logging
from typing import Tuple, Dict, Optional
from app.config import settings

# 配置日志
logger = logging.getLogger(__name__)

class SSHService:
    def __init__(self):
        self.host = settings.ssh_host
        self.port = settings.ssh_port
        self.username = settings.ssh_username
        self.password = settings.ssh_password
        self.key_path = settings.ssh_key_path
    
    def _get_client(self) -> paramiko.SSHClient:
        """获取 SSH 客户端连接"""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if self.key_path:
            client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                key_filename=self.key_path
            )
        else:
            client.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password
            )
        return client
    
    def execute_command(self, command: str, background: bool = False, timeout: int = 30) -> Tuple[str, str, int]:
        """
        执行命令
        返回: (stdout, stderr, return_code)
        """
        logger.info(f"[SSH] 连接到服务器: {self.host}:{self.port}, 用户: {self.username}")
        logger.info(f"[SSH] 执行命令: {command[:200]}..." if len(command) > 200 else f"[SSH] 执行命令: {command}")
        logger.info(f"[SSH] 后台执行: {background}, 超时: {timeout}秒")
        
        client = self._get_client()
        try:
            if background:
                # 后台执行，先尝试获取初始输出
                logger.info("[SSH] 后台执行模式，尝试获取初始输出...")
                stdin, stdout, stderr = client.exec_command(command)
                
                # 等待一小段时间获取初始输出
                import time
                time.sleep(2)  # 等待2秒获取初始输出
                
                # 读取初始输出（非阻塞）
                stdout_text = ""
                stderr_text = ""
                if stdout.channel.recv_ready():
                    stdout_text = stdout.read().decode('utf-8', errors='ignore')
                if stderr.channel.recv_ready():
                    stderr_text = stderr.read().decode('utf-8', errors='ignore')
                
                logger.info(f"[SSH] 后台命令初始输出 (stdout): {stdout_text[:500]}")
                logger.info(f"[SSH] 后台命令初始输出 (stderr): {stderr_text[:500]}")
                
                return stdout_text, stderr_text, 0
            else:
                logger.info("[SSH] 同步执行模式，等待命令完成...")
                stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
                exit_status = stdout.channel.recv_exit_status()
                stdout_text = stdout.read().decode('utf-8', errors='ignore')
                stderr_text = stderr.read().decode('utf-8', errors='ignore')
                
                logger.info(f"[SSH] 命令执行完成，退出码: {exit_status}")
                logger.info(f"[SSH] 标准输出 (stdout): {stdout_text[:1000]}")
                logger.info(f"[SSH] 标准错误 (stderr): {stderr_text[:1000]}")
                
                if exit_status != 0:
                    logger.warning(f"[SSH] 命令执行失败，退出码: {exit_status}, 错误: {stderr_text}")
                
                return stdout_text, stderr_text, exit_status
        except Exception as e:
            logger.error(f"[SSH] 执行命令时发生异常: {str(e)}", exc_info=True)
            raise
        finally:
            client.close()
            logger.info("[SSH] SSH连接已关闭")
    
    def execute_chat_script(self, config: Dict, script_path: str, timeout: int = 300) -> Dict:
        """
        执行对话推理脚本（Python脚本方式）
        参数:
            config: 包含 base_model_path, adapter_path, messages, temperature, max_tokens 的字典
            script_path: 远程服务器上脚本的路径
            timeout: 超时时间（秒），默认 300 秒
        返回: 推理结果字典 {"role": "assistant", "content": "..."}
        """
        # 将配置序列化为 JSON
        config_json = json.dumps(config, ensure_ascii=False)
        # 构建命令（通过命令行参数传递 JSON，使用单引号包裹）
        command = f"python3 {script_path} '{config_json}'"
        
        stdout, stderr, return_code = self.execute_command(command, background=False, timeout=timeout)
        
        if return_code != 0:
            raise Exception(f"推理脚本执行失败: {stderr}")
        
        # 解析 JSON 输出
        try:
            result = json.loads(stdout)
            return result
        except json.JSONDecodeError as e:
            raise Exception(f"解析推理结果失败: {stdout}, 错误: {str(e)}")
    
    def execute_chat_cli(self, config: Dict, template: str = "qwen2", timeout: int = 300) -> Dict:
        """
        通过交互式CLI执行对话推理（使用pexpect在远程服务器上）
        参数:
            config: 包含 base_model_path, adapter_path, messages 的字典
            template: 模板名称，默认 qwen2
            timeout: 超时时间（秒），默认 300 秒
        返回: 推理结果字典 {"role": "assistant", "content": "..."}
        
        注意：这个方法需要在远程服务器上有一个包装脚本，使用pexpect与llamafactory-cli交互
        """
        logger.info("[SSH] 使用CLI模式执行对话推理")
        
        # 提取用户消息（只取最后一条用户消息用于单次对话）
        messages = config.get("messages", [])
        user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content")
                break
        
        if not user_message:
            raise ValueError("消息列表中未找到用户消息")
        
        # 构建包装脚本调用命令
        # 这个命令会调用远程服务器上的pexpect包装脚本
        base_model_path = config.get("base_model_path")
        adapter_path = config.get("adapter_path")
        
        # 使用远程包装脚本（假设脚本已部署）
        # 脚本需要通过参数接收配置，并使用pexpect与llamafactory-cli chat交互
        wrapper_script = settings.chat_script_path  # 这里复用chat_script_path作为包装脚本路径
        
        # 确保使用绝对路径
        if not wrapper_script.startswith('/'):
            # 如果是相对路径，使用remote_work_dir作为基础
            wrapper_script = f"{settings.remote_work_dir}/{wrapper_script}"
        
        # 构建JSON配置
        cli_config = {
            "base_model_path": base_model_path,
            "adapter_path": adapter_path,
            "template": template,
            "message": user_message
        }
        config_json = json.dumps(cli_config, ensure_ascii=False)
        
        # 使用base64编码JSON，避免shell解析问题
        import base64
        config_b64 = base64.b64encode(config_json.encode('utf-8')).decode('ascii')
        
        # 构建完整命令，包括：
        # 1. 切换到工作目录（确保路径正确）
        # 2. 激活conda环境（如果配置了）
        # 3. 使用绝对路径执行脚本，传递base64编码的JSON
        # 注意：使用bash -l -c来确保加载用户的login shell配置（.bashrc, .bash_profile等）
        work_dir = settings.remote_work_dir
        conda_env = getattr(settings, 'conda_env', None)
        
        # 构建命令前缀（切换目录和激活conda环境）
        cmd_parts = []
        cmd_parts.append(f"cd {work_dir}")
        
        # 如果配置了conda环境，先激活
        if conda_env:
            # 尝试多种方式激活conda环境
            cmd_parts.append("source ~/.bashrc 2>/dev/null || true")  # 加载用户配置
            cmd_parts.append("source $(conda info --base)/etc/profile.d/conda.sh 2>/dev/null || true")  # 加载conda
            cmd_parts.append(f"conda activate {conda_env} 2>/dev/null || source activate {conda_env} 2>/dev/null || true")
        
        # 执行Python脚本，传递base64编码的JSON（使用双引号包裹base64字符串，避免shell解析问题）
        cmd_parts.append(f'python3 {wrapper_script} "{config_b64}"')
        
        # 组合命令（使用&&确保每一步成功）
        inner_command = " && ".join(cmd_parts)
        # 使用bash -l -c来执行，确保加载完整的用户环境
        # 注意：使用单引号包裹整个命令，内部使用双引号包裹base64字符串
        command = f"bash -l -c '{inner_command}'"
        logger.info(f"[SSH] 执行CLI包装命令: {command[:200]}...")
        
        stdout, stderr, return_code = self.execute_command(command, background=False, timeout=timeout)
        
        if return_code != 0:
            logger.error(f"[SSH] CLI执行失败，返回码: {return_code}, stderr: {stderr}")
            raise Exception(f"CLI执行失败: {stderr}")
        
        # 解析JSON输出
        try:
            # 尝试从stdout中提取JSON（可能有其他输出）
            stdout_lines = stdout.strip().split('\n')
            # 查找最后一个JSON对象
            json_output = None
            for line in reversed(stdout_lines):
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    try:
                        json_output = json.loads(line)
                        break
                    except:
                        continue
            
            if not json_output:
                # 如果找不到JSON，尝试解析整个stdout
                json_output = json.loads(stdout.strip())
            
            return json_output
        except json.JSONDecodeError as e:
            logger.error(f"[SSH] 解析JSON失败，stdout: {stdout[:500]}")
            # 如果无法解析为JSON，尝试从输出中提取Assistant回复
            # llamafactory-cli的输出格式通常是: "Assistant: <回复内容>"
            assistant_match = None
            for line in stdout.split('\n'):
                if 'Assistant:' in line:
                    assistant_match = line.split('Assistant:', 1)[1].strip()
                    break
            
            if assistant_match:
                return {"role": "assistant", "content": assistant_match}
            
            raise Exception(f"解析推理结果失败: {stdout}, 错误: {str(e)}")
    
    def check_process(self, process_id: str) -> bool:
        """
        检查进程是否运行
        """
        command = f"ps -p {process_id} > /dev/null 2>&1 && echo 'running' || echo 'stopped'"
        stdout, stderr, return_code = self.execute_command(command)
        return "running" in stdout
    
    def read_file(self, file_path: str) -> str:
        """
        读取远程文件内容
        """
        logger.info(f"[SSH] 读取远程文件: {file_path}")
        command = f"cat {file_path}"
        stdout, stderr, return_code = self.execute_command(command)
        if return_code != 0:
            logger.error(f"[SSH] 读取文件失败，路径: {file_path}, 错误: {stderr}")
            raise Exception(f"读取文件失败: {stderr}")
        logger.info(f"[SSH] 文件读取成功，大小: {len(stdout)} 字符")
        return stdout
    
    def upload_file(self, local_path: str, remote_path: str):
        """
        上传文件到远程服务器（使用 SFTP）
        """
        logger.info(f"[SSH] 上传文件: {local_path} -> {remote_path}")
        client = self._get_client()
        try:
            sftp = client.open_sftp()
            # 确保远程目录存在
            remote_dir = '/'.join(remote_path.split('/')[:-1])
            logger.info(f"[SSH] 创建远程目录: {remote_dir}")
            self.execute_command(f"mkdir -p {remote_dir}")
            logger.info(f"[SSH] 开始SFTP上传...")
            sftp.put(local_path, remote_path)
            sftp.close()
            logger.info(f"[SSH] 文件上传成功")
        except Exception as e:
            logger.error(f"[SSH] 文件上传失败: {str(e)}", exc_info=True)
            raise
        finally:
            client.close()

