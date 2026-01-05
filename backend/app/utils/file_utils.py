import os
from typing import Optional

def get_file_size(file_path: str) -> int:
    """获取文件大小（字节）"""
    return os.path.getsize(file_path)

def ensure_dir(dir_path: str):
    """确保目录存在"""
    os.makedirs(dir_path, exist_ok=True)

