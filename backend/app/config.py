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
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

