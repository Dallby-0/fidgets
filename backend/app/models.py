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
    """
    训练任务创建请求模型

    字段与训练命令参数的对应关系：
    - name:                任务名称（只存数据库，不参与命令）
    - model_name:          --model_name_or_path
    - dataset_path:        远程数据集路径（会在训练前被拷贝为 current_dataset.json）
    - stage:               --stage（默认 sft）
    - template:            --template（默认 qwen2）
    - epochs:              --num_train_epochs
    - learning_rate:       --learning_rate
    - batch_size:          --per_device_train_batch_size
    - gradient_accumulation_steps: --gradient_accumulation_steps
    - fp16:                是否添加 --fp16
    - output_dir:          --output_dir
    """

    name: str
    model_name: str
    dataset_path: str

    # 训练阶段和模板
    stage: Optional[str] = "sft"
    template: Optional[str] = "qwen2"

    # 训练超参数
    epochs: Optional[float] = 3.0  # 对应 num_train_epochs
    learning_rate: Optional[float] = 5e-5
    batch_size: Optional[int] = 4  # per_device_train_batch_size
    gradient_accumulation_steps: Optional[int] = 4

    # 训练配置
    fp16: Optional[bool] = True
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

# 数据集生成相关模型
class DatasetGenerateRequest(BaseModel):
    topic: str
    filename: Optional[str] = None  # 可选的文件名，如果不提供则使用话题前10个字符

