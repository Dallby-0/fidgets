from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # SSH 配置
    ssh_host: str
    ssh_port: int = 22
    ssh_username: str
    ssh_password: Optional[str] = None
    ssh_key_path: Optional[str] = None
    remote_work_dir: str
    
    # 应用配置
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    # 文件存储配置
    remote_user_data_dir: str
    max_upload_size: int = 104857600  # 100MB
    
    # 对话推理配置
    chat_script_path: str
    chat_timeout: int = 300
    # 使用交互式CLI还是Python脚本（"cli" 或 "script"）
    chat_mode: str = "cli"
    # LlamaFactory CLI路径（如果使用cli模式）
    llamafactory_cli_path: str = "llamafactory-cli"
    # Conda环境名称（如果需要激活conda环境，留空则不激活）
    conda_env: Optional[str] = None
    
    # DeepSeek API配置
    deepseek_api_key: Optional[str] = None
    deepseek_api_url: str = "https://api.deepseek.com/v1/chat/completions"
    deepseek_model: str = "deepseek-reasoner"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

