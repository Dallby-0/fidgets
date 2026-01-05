from app.models import ChatRequest, ChatResponse
from app.services.ssh_service import SSHService
from app.services.file_service import FileService
from sqlalchemy.orm import Session
from app.config import settings

class ChatService:
    def __init__(self):
        self.ssh_service = SSHService()
        self.file_service = FileService()
        self.chat_script_path = settings.chat_script_path
    
    def chat_completion(self, db: Session, user_id: str, request: ChatRequest) -> ChatResponse:
        """执行对话推理"""
        # 验证模型路径属于当前用户
        model_info = self.file_service.get_model_by_path(db, request.model_path, user_id)
        if not model_info:
            raise ValueError("模型不存在或无权访问")
        
        # 获取基础模型路径
        base_model_path = model_info.base_model_path
        if not base_model_path:
            raise ValueError("模型缺少基础模型路径信息")
        
        # 构建推理配置
        config = {
            "base_model_path": base_model_path,
            "adapter_path": request.model_path,
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens
        }
        
        # 执行推理脚本
        result = self.ssh_service.execute_chat_script(
            config=config,
            script_path=self.chat_script_path,
            timeout=settings.chat_timeout
        )
        
        return ChatResponse(**result)

