import paramiko
import json
from typing import Tuple, Dict, Optional
from app.config import settings

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
        client = self._get_client()
        try:
            if background:
                # 后台执行，立即返回
                stdin, stdout, stderr = client.exec_command(command)
                return "", "", 0
            else:
                stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
                exit_status = stdout.channel.recv_exit_status()
                stdout_text = stdout.read().decode('utf-8')
                stderr_text = stderr.read().decode('utf-8')
                return stdout_text, stderr_text, exit_status
        finally:
            client.close()
    
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
        command = f"cat {file_path}"
        stdout, stderr, return_code = self.execute_command(command)
        if return_code != 0:
            raise Exception(f"读取文件失败: {stderr}")
        return stdout
    
    def upload_file(self, local_path: str, remote_path: str):
        """
        上传文件到远程服务器（使用 SFTP）
        """
        client = self._get_client()
        try:
            sftp = client.open_sftp()
            # 确保远程目录存在
            remote_dir = '/'.join(remote_path.split('/')[:-1])
            self.execute_command(f"mkdir -p {remote_dir}")
            sftp.put(local_path, remote_path)
            sftp.close()
        finally:
            client.close()

