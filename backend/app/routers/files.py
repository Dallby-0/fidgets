from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import tempfile
import os
from app.database import get_db
from app.dependencies import get_current_user
from app.db_models import UserDB
from app.services.file_service import FileService
from app.models import DatasetFile, ModelFile

router = APIRouter(prefix="/api/files", tags=["files"])

@router.post("/datasets", response_model=DatasetFile, status_code=status.HTTP_201_CREATED)
def upload_dataset(
    file: UploadFile = File(...),
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传数据集文件"""
    file_service = FileService()
    
    # 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        content = file.file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
        file_size = len(content)
    
    try:
        db_file = file_service.upload_dataset_file(
            db=db,
            user_id=current_user.user_id,
            filename=file.filename,
            local_file_path=tmp_file_path,
            file_size=file_size
        )
        return DatasetFile(
            file_id=db_file.file_id,
            user_id=db_file.user_id,
            filename=db_file.filename,
            file_path=db_file.file_path,
            size=db_file.size,
            created_at=db_file.created_at
        )
    finally:
        # 删除临时文件
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

@router.get("/datasets", response_model=list[DatasetFile])
def get_datasets(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的数据集文件列表"""
    file_service = FileService()
    files = file_service.get_user_datasets(db, current_user.user_id)
    return [
        DatasetFile(
            file_id=f.file_id,
            user_id=f.user_id,
            filename=f.filename,
            file_path=f.file_path,
            size=f.size,
            created_at=f.created_at
        )
        for f in files
    ]

@router.delete("/datasets/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(
    file_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除数据集文件"""
    file_service = FileService()
    success = file_service.delete_dataset_file(db, file_id, current_user.user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")
    return None

@router.get("/models", response_model=list[ModelFile])
def get_models(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的模型文件列表"""
    file_service = FileService()
    models = file_service.get_user_models(db, current_user.user_id)
    return [
        ModelFile(
            model_id=m.model_id,
            user_id=m.user_id,
            name=m.name,
            model_path=m.model_path,
            base_model_path=m.base_model_path,
            task_id=m.task_id,
            size=m.size,
            created_at=m.created_at
        )
        for m in models
    ]

@router.get("/models/available", response_model=list[ModelFile])
def get_available_models(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取可用于对话的模型列表"""
    file_service = FileService()
    models = file_service.get_user_models(db, current_user.user_id)
    # 只返回有基础模型路径的模型
    available = [m for m in models if m.base_model_path]
    return [
        ModelFile(
            model_id=m.model_id,
            user_id=m.user_id,
            name=m.name,
            model_path=m.model_path,
            base_model_path=m.base_model_path,
            task_id=m.task_id,
            size=m.size,
            created_at=m.created_at
        )
        for m in available
    ]

