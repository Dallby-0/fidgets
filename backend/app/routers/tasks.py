import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from app.database import get_db
from app.dependencies import get_current_user
from app.db_models import UserDB, TaskDB
from app.models import TaskCreate, Task
from app.services.task_service import TaskService
from app.services.file_service import FileService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

# 硬编码的模型列表
AVAILABLE_MODELS = {
    "Qwen2-0.5B": {
        "model_path": "/root/autodl-tmp/Qwen2-0.5B-Instruct",
        "template": "qwen2"
    }
}

@router.get("/models", response_model=List[Dict[str, str]])
def get_available_models():
    """获取可用的模型列表"""
    return [
        {
            "name": name,
            "model_path": info["model_path"],
            "template": info["template"]
        }
        for name, info in AVAILABLE_MODELS.items()
    ]

@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建训练任务"""
    logger.info(f"[API] 创建训练任务，用户: {current_user.user_id}, 任务名: {task_data.name}")
    
    # 验证模型名称是否有效
    if task_data.model_name not in AVAILABLE_MODELS:
        logger.warning(f"[API] 无效的模型名称: {task_data.model_name}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"无效的模型名称: {task_data.model_name}")
    
    # 根据模型名称获取模型路径和模板
    model_info = AVAILABLE_MODELS[task_data.model_name]
    model_path = model_info["model_path"]
    template = model_info["template"]
    
    # 如果用户提供了模板，使用用户提供的模板（向后兼容），否则使用模型默认模板
    if task_data.template:
        template = task_data.template
    
    logger.info(f"[API] 使用模型: {task_data.model_name}, 路径: {model_path}, 模板: {template}")
    
    # 验证数据集文件是否存在（通过路径验证）
    file_service = FileService()
    datasets = file_service.get_user_datasets(db, current_user.user_id)
    dataset_paths = [d.file_path for d in datasets]
    logger.info(f"[API] 用户数据集路径列表: {dataset_paths}")
    logger.info(f"[API] 请求的数据集路径: {task_data.dataset_path}")
    
    if task_data.dataset_path not in dataset_paths:
        logger.warning(f"[API] 数据集文件不存在: {task_data.dataset_path}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="数据集文件不存在")
    
    task_service = TaskService()
    try:
        # 创建修改后的task_data，使用模型路径和模板
        task_data_with_path = TaskCreate(
            name=task_data.name,
            model_name=task_data.model_name,  # 存储模型名称，不是路径
            dataset_path=task_data.dataset_path,
            stage=task_data.stage,
            template=template,  # 使用模型对应的模板
            epochs=task_data.epochs,
            learning_rate=task_data.learning_rate,
            batch_size=task_data.batch_size,
            gradient_accumulation_steps=task_data.gradient_accumulation_steps,
            fp16=task_data.fp16,
            output_dir=None  # 不使用用户提供的输出目录
        )
        
        # 传递模型路径给service（用于实际训练命令）
        db_task = task_service.create_task(db, current_user.user_id, task_data_with_path, model_path=model_path)
        logger.info(f"[API] 训练任务创建成功，任务ID: {db_task.task_id}")
        return Task(
            task_id=db_task.task_id,
            user_id=db_task.user_id,
            name=db_task.name,
            model_name=db_task.model_name,  # 这里存储的是模型名称
            dataset_path=db_task.dataset_path,
            epochs=db_task.epochs,
            learning_rate=db_task.learning_rate,
            batch_size=db_task.batch_size,
            output_dir=db_task.output_dir,
            status=db_task.status,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at
        )
    except Exception as e:
        logger.error(f"[API] 创建训练任务失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("", response_model=List[Task])
def get_tasks(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的任务列表"""
    task_service = TaskService()
    tasks = task_service.get_user_tasks(db, current_user.user_id)
    return [
        Task(
            task_id=t.task_id,
            user_id=t.user_id,
            name=t.name,
            model_name=t.model_name,
            dataset_path=t.dataset_path,
            epochs=t.epochs,
            learning_rate=t.learning_rate,
            batch_size=t.batch_size,
            output_dir=t.output_dir,
            status=t.status,
            created_at=t.created_at,
            updated_at=t.updated_at
        )
        for t in tasks
    ]

@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取任务详情"""
    task_service = TaskService()
    task = task_service.get_task(db, task_id, current_user.user_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    
    # 检查任务状态，如果完成则自动添加模型
    if task.status == "running":
        # 简单检查：尝试读取日志文件判断是否完成（最小实现）
        try:
            logs = task_service.get_task_logs(db, task_id, current_user.user_id)
            if "Training completed" in logs or "训练完成" in logs:
                task.status = "completed"
                db.commit()
        except:
            pass
    
    # 如果任务完成，自动添加模型到模型列表
    if task.status == "completed":
        file_service = FileService()
        existing_model = file_service.get_model_by_path(db, task.output_dir, current_user.user_id)
        if not existing_model:
            # 将模型名称映射回路径（用于base_model_path）
            base_model_path = task.model_name  # 默认使用模型名称
            if task.model_name in AVAILABLE_MODELS:
                base_model_path = AVAILABLE_MODELS[task.model_name]["model_path"]
            
            file_service.add_model_file(
                db=db,
                user_id=current_user.user_id,
                name=f"{task.name}_model",
                model_path=task.output_dir,
                base_model_path=base_model_path,  # 使用模型路径作为基础模型路径
                task_id=task.task_id
            )
    
    return Task(
        task_id=task.task_id,
        user_id=task.user_id,
        name=task.name,
        model_name=task.model_name,
        dataset_path=task.dataset_path,
        epochs=task.epochs,
        learning_rate=task.learning_rate,
        batch_size=task.batch_size,
        output_dir=task.output_dir,
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

@router.get("/{task_id}/logs")
def get_task_logs(
    task_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取任务日志"""
    task_service = TaskService()
    task = task_service.get_task(db, task_id, current_user.user_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在")
    
    logs = task_service.get_task_logs(db, task_id, current_user.user_id)
    return {"logs": logs}
