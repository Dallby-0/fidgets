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
        执行对话推理脚本
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

