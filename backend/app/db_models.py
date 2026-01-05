from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class UserDB(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class TaskDB(Base):
    __tablename__ = "tasks"
    task_id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    dataset_path = Column(String, nullable=False)
    epochs = Column(Integer, default=3)
    learning_rate = Column(Float, default=5e-5)
    batch_size = Column(Integer, default=4)
    output_dir = Column(String, nullable=False)
    status = Column(String, default="pending")
    ssh_command = Column(Text, nullable=True)
    process_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DatasetFileDB(Base):
    __tablename__ = "dataset_files"
    file_id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ModelFileDB(Base):
    __tablename__ = "model_files"
    model_id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    model_path = Column(String, nullable=False)
    base_model_path = Column(String, nullable=True)
    task_id = Column(String, ForeignKey("tasks.task_id"), nullable=True)
    size = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

