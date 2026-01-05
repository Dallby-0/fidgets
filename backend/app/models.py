from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# 用户相关模型
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username_or_email: str
    password: str
    remember_me: Optional[bool] = False

class User(BaseModel):
    user_id: str
    username: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

# 任务相关模型
class TaskCreate(BaseModel):
    name: str
    model_name: str
    dataset_path: str
    epochs: Optional[int] = 3
    learning_rate: Optional[float] = 5e-5
    batch_size: Optional[int] = 4
    output_dir: Optional[str] = None

class Task(BaseModel):
    task_id: str
    user_id: str
    name: str
    model_name: str
    dataset_path: str
    epochs: int
    learning_rate: float
    batch_size: int
    output_dir: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 文件相关模型
class DatasetFile(BaseModel):
    file_id: str
    user_id: str
    filename: str
    file_path: str
    size: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ModelFile(BaseModel):
    model_id: str
    user_id: str
    name: str
    model_path: str
    base_model_path: Optional[str] = None
    task_id: Optional[str] = None
    size: Optional[int] = None
    created_at: datetime
    
    model_config = {
        'protected_namespaces': (),
        'from_attributes': True
    }

# 对话相关模型
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model_path: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048

class ChatResponse(BaseModel):
    role: str
    content: str

