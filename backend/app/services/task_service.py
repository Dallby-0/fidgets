import uuid
import logging
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db_models import TaskDB
from app.models import TaskCreate, Task
from app.services.ssh_service import SSHService
from app.config import settings

logger = logging.getLogger(__name__)

class TaskService:
    def __init__(self):
        self.ssh_service = SSHService()
    
    def create_task(self, db: Session, user_id: str, task_data: TaskCreate) -> TaskDB:
        """创建任务并启动执行"""
        # 使用默认模型路径（如果未提供）
        model_name = task_data.model_name or settings.default_model_path
        logger.info(f"[训练任务] 使用模型路径: {model_name}")
        
        # 生成输出目录
        if not task_data.output_dir:
            task_id = str(uuid.uuid4())
            output_dir = f"{settings.remote_user_data_dir}/{user_id}/models/{task_id}"
        else:
            output_dir = task_data.output_dir
        logger.info(f"[训练任务] 使用输出目录: {output_dir}")

        # 在远程服务器上准备当前数据集文件：复制为 current_dataset.json
        current_dataset_path = f"{settings.remote_work_dir}/current_dataset.json"
        copy_command = f"cp {task_data.dataset_path} {current_dataset_path}"
        logger.info(f"[训练任务] 准备数据集：{task_data.dataset_path} -> {current_dataset_path}")
        try:
            stdout_cp, stderr_cp, rc_cp = self.ssh_service.execute_command(copy_command, background=False)
            logger.info(f"[训练任务] 拷贝数据集返回码: {rc_cp}")
            logger.info(f"[训练任务] 拷贝数据集 stdout: {stdout_cp[:500] if stdout_cp else '(空)'}")
            logger.info(f"[训练任务] 拷贝数据集 stderr: {stderr_cp[:500] if stderr_cp else '(空)'}")
            if rc_cp != 0:
                raise Exception(f"远程拷贝数据集失败: {stderr_cp}")
        except Exception as e:
            logger.error(f"[训练任务] 远程拷贝数据集失败: {str(e)}", exc_info=True)
            raise

        # 确保输出目录存在（在构建命令之前）
        mkdir_command = f"mkdir -p {output_dir}"
        logger.info(f"[训练任务] 创建输出目录: {output_dir}")
        try:
            stdout_mkdir, stderr_mkdir, rc_mkdir = self.ssh_service.execute_command(mkdir_command, background=False)
            if rc_mkdir != 0:
                logger.warning(f"[训练任务] 创建输出目录失败: {stderr_mkdir}")
                raise Exception(f"创建输出目录失败: {stderr_mkdir}")
        except Exception as e:
            logger.error(f"[训练任务] 创建输出目录失败: {str(e)}", exc_info=True)
            raise
        
        # 构建训练命令（此时 --dataset 将固定使用 current_dataset）
        command = self.build_training_command(task_data, output_dir, model_name)
        
        # 创建任务记录
        db_task = TaskDB(
            user_id=user_id,
            name=task_data.name,
            model_name=model_name,  # 使用处理后的模型路径（默认值或用户提供的值）
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
            logger.info(f"[训练任务] 开始执行训练命令，任务ID: {db_task.task_id}")
            stdout, stderr, return_code = self.ssh_service.execute_command(command, background=True)
            
            logger.info(f"[训练任务] 命令执行返回 - 退出码: {return_code}")
            logger.info(f"[训练任务] 命令执行返回 - stdout: {stdout[:500] if stdout else '(空)'}")
            logger.info(f"[训练任务] 命令执行返回 - stderr: {stderr[:500] if stderr else '(空)'}")
            
            # 保存执行结果到数据库（可选，用于调试）
            if stdout or stderr:
                debug_info = f"stdout: {stdout[:200]}\nstderr: {stderr[:200]}"
                # 可以扩展 TaskDB 添加 debug_info 字段，这里先记录到日志
            
            db_task.status = "running"
            db.commit()
            logger.info(f"[训练任务] 任务状态已更新为 running，任务ID: {db_task.task_id}")
        except Exception as e:
            logger.error(f"[训练任务] 启动训练任务失败: {str(e)}", exc_info=True)
            db_task.status = "failed"
            db.commit()
            raise Exception(f"启动训练任务失败: {str(e)}")
        
        return db_task
    
    def build_training_command(self, task_data: TaskCreate, output_dir: str, model_name: str) -> str:
        """构建 LlamaFactory 训练命令

        目标命令示例（用户在云端测试通过的版本）：

        llamafactory-cli train \
          --stage sft \
          --model_name_or_path /root/autodl-tmp/Qwen2-0.5B-Instruct \
          --dataset current_dataset \
          --template qwen2 \
          --finetuning_type lora \
          --output_dir /root/autodl-tmp/out \
          --overwrite_cache \
          --per_device_train_batch_size 4 \
          --gradient_accumulation_steps 4 \
          --learning_rate 5e-5 \
          --num_train_epochs 3.0 \
          --fp16 \
          --plot_loss \
          --do_train
        """
        work_dir = settings.remote_work_dir
        dataset_name = "current_dataset"

        # 构建命令字符串
        # 使用 bash -l -c 确保使用login shell并加载环境变量（如.bashrc中的PATH）
        # 将多行命令合并为单行，避免SSH解析问题
        # 注意：使用双引号包裹bash -c的参数，避免单引号冲突
        train_cmd = (
            f"cd {work_dir} && "
            f"nohup llamafactory-cli train "
            f"--stage {task_data.stage or 'sft'} "
            f"--model_name_or_path {model_name} "
            f"--dataset {dataset_name} "
            f"--template {task_data.template or 'qwen2'} "
            f"--finetuning_type lora "
            f"--output_dir {output_dir} "
            f"--overwrite_cache "
            f"--per_device_train_batch_size {task_data.batch_size or 4} "
            f"--gradient_accumulation_steps {task_data.gradient_accumulation_steps or 4} "
            f"--learning_rate {task_data.learning_rate or 5e-5} "
            f"--num_train_epochs {task_data.epochs or 3.0} "
            f"--fp16 "
            f"--cutoff_len 1024 "
            f"--plot_loss "
            f"--do_train > {output_dir}/train.log 2>&1 &"
        )
        
        # 使用 bash -l -c 执行（-l表示login shell，会加载.bashrc等配置文件）
        # 使用双引号包裹命令，避免单引号冲突
        command = f'bash -l -c "{train_cmd}"'

        logger.info(f"[训练任务] 构建训练命令:")
        logger.info(f"[训练任务] 工作目录: {work_dir}")
        logger.info(f"[训练任务] 模型: {model_name}")
        logger.info(f"[训练任务] 数据集(逻辑名): {dataset_name}，源路径: {task_data.dataset_path}")
        logger.info(f"[训练任务] 输出目录: {output_dir}")
        logger.info(f"[训练任务] 完整命令: {command}")

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
        logger.info(f"[训练任务] 获取任务日志，任务ID: {task_id}")
        task = self.get_task(db, task_id, user_id)
        if not task:
            logger.warning(f"[训练任务] 任务不存在: {task_id}")
            return ""
        
        log_file = f"{task.output_dir}/train.log"
        logger.info(f"[训练任务] 日志文件路径: {log_file}")
        try:
            logs = self.ssh_service.read_file(log_file)
            logger.info(f"[训练任务] 成功读取日志，长度: {len(logs)} 字符")
            return logs
        except Exception as e:
            logger.error(f"[训练任务] 读取日志失败: {str(e)}", exc_info=True)
            return f"日志文件不存在或无法读取: {str(e)}"

