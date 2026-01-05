import logging
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db_models import DatasetFileDB, ModelFileDB
from app.services.ssh_service import SSHService
from app.config import settings

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self):
        self.ssh_service = SSHService()
    
    def upload_dataset_file(
        self, 
        db: Session, 
        user_id: str, 
        filename: str, 
        local_file_path: str,
        file_size: int
    ) -> DatasetFileDB:
        """上传数据集文件到远程服务器"""
        logger.info(f"[文件服务] 上传数据集文件，用户: {user_id}, 文件名: {filename}, 大小: {file_size} 字节")
        
        # 生成远程文件路径
        remote_dir = f"{settings.remote_user_data_dir}/{user_id}/datasets"
        remote_file_path = f"{remote_dir}/{filename}"
        logger.info(f"[文件服务] 远程文件路径: {remote_file_path}")
        
        # 上传文件
        try:
            self.ssh_service.upload_file(local_file_path, remote_file_path)
            logger.info(f"[文件服务] 文件上传成功")
        except Exception as e:
            logger.error(f"[文件服务] 文件上传失败: {str(e)}", exc_info=True)
            raise
        
        # 保存文件信息到数据库
        db_file = DatasetFileDB(
            user_id=user_id,
            filename=filename,
            file_path=remote_file_path,
            size=file_size
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        logger.info(f"[文件服务] 文件信息已保存到数据库，文件ID: {db_file.file_id}")
        return db_file
    
    def get_user_datasets(self, db: Session, user_id: str) -> List[DatasetFileDB]:
        """获取用户的数据集文件列表"""
        return db.query(DatasetFileDB).filter(DatasetFileDB.user_id == user_id).all()
    
    def get_dataset_by_id(self, db: Session, file_id: str, user_id: str) -> Optional[DatasetFileDB]:
        """根据ID获取数据集文件（验证用户权限）"""
        return db.query(DatasetFileDB).filter(
            DatasetFileDB.file_id == file_id,
            DatasetFileDB.user_id == user_id
        ).first()
    
    def delete_dataset_file(self, db: Session, file_id: str, user_id: str) -> bool:
        """删除数据集文件"""
        db_file = self.get_dataset_by_id(db, file_id, user_id)
        if not db_file:
            return False
        
        # 删除远程文件（可选，最小实现可以只删除数据库记录）
        try:
            self.ssh_service.execute_command(f"rm -f {db_file.file_path}")
        except:
            pass  # 忽略删除错误
        
        db.delete(db_file)
        db.commit()
        return True
    
    def add_model_file(
        self,
        db: Session,
        user_id: str,
        name: str,
        model_path: str,
        base_model_path: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> ModelFileDB:
        """添加模型文件记录"""
        db_model = ModelFileDB(
            user_id=user_id,
            name=name,
            model_path=model_path,
            base_model_path=base_model_path,
            task_id=task_id
        )
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return db_model
    
    def get_user_models(self, db: Session, user_id: str) -> List[ModelFileDB]:
        """获取用户的模型文件列表"""
        return db.query(ModelFileDB).filter(ModelFileDB.user_id == user_id).all()
    
    def get_model_by_path(self, db: Session, model_path: str, user_id: str) -> Optional[ModelFileDB]:
        """根据路径获取模型文件（验证用户权限）"""
        return db.query(ModelFileDB).filter(
            ModelFileDB.model_path == model_path,
            ModelFileDB.user_id == user_id
        ).first()

