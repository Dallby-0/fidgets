import uuid
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db_models import TaskDB
from app.models import TaskCreate, Task
from app.services.ssh_service import SSHService
from app.config import settings

class TaskService:
    def __init__(self):
        self.ssh_service = SSHService()
    
    def create_task(self, db: Session, user_id: str, task_data: TaskCreate) -> TaskDB:
        """创建任务并启动执行"""
        # 生成输出目录
        if not task_data.output_dir:
            task_id = str(uuid.uuid4())
            output_dir = f"{settings.remote_user_data_dir}/{user_id}/models/{task_id}"
        else:
            output_dir = task_data.output_dir
        
        # 构建训练命令
        command = self.build_training_command(task_data, output_dir)
        
        # 创建任务记录
        db_task = TaskDB(
            user_id=user_id,
            name=task_data.name,
            model_name=task_data.model_name,
            dataset_path=task_data.dataset_path,
            epochs=task_data.epochs,
            learning_rate=task_data.learning_rate,
            batch_size=task_data.batch_size,
            output_dir=output_dir,
            status="pending",
            ssh_command=command
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        
        # 执行训练命令（后台执行）
        try:
            self.ssh_service.execute_command(command, background=True)
            db_task.status = "running"
            db.commit()
        except Exception as e:
            db_task.status = "failed"
            db.commit()
            raise Exception(f"启动训练任务失败: {str(e)}")
        
        return db_task
    
    def build_training_command(self, task_data: TaskCreate, output_dir: str) -> str:
        """构建 LlamaFactory 训练命令"""
        work_dir = settings.remote_work_dir
        command = f"""cd {work_dir} && nohup llamafactory-cli train \
    --model_name_or_path {task_data.model_name} \
    --dataset {task_data.dataset_path} \
    --template default \
    --finetuning_type lora \
    --output_dir {output_dir} \
    --num_train_epochs {task_data.epochs} \
    --learning_rate {task_data.learning_rate} \
    --per_device_train_batch_size {task_data.batch_size} \
    --cutoff_len 1024 \
    --plot_loss > {output_dir}/train.log 2>&1 &"""
        return command
    
    def get_task(self, db: Session, task_id: str, user_id: str) -> Optional[TaskDB]:
        """获取任务详情（验证用户权限）"""
        return db.query(TaskDB).filter(
            TaskDB.task_id == task_id,
            TaskDB.user_id == user_id
        ).first()
    
    def get_user_tasks(self, db: Session, user_id: str) -> List[TaskDB]:
        """获取用户的任务列表"""
        return db.query(TaskDB).filter(TaskDB.user_id == user_id).order_by(TaskDB.created_at.desc()).all()
    
    def get_task_logs(self, db: Session, task_id: str, user_id: str) -> str:
        """获取任务日志"""
        task = self.get_task(db, task_id, user_id)
        if not task:
            return ""
        
        log_file = f"{task.output_dir}/train.log"
        try:
            logs = self.ssh_service.read_file(log_file)
            return logs
        except:
            return "日志文件不存在或无法读取"

