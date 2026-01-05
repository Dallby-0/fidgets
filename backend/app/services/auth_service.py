from sqlalchemy.orm import Session
from typing import Optional
from app.db_models import UserDB
from app.models import UserRegister, User
from app.utils.security import verify_password, get_password_hash, create_access_token
from datetime import timedelta

def register_user(db: Session, user_data: UserRegister) -> UserDB:
    """注册新用户"""
    # 检查用户名是否已存在
    if db.query(UserDB).filter(UserDB.username == user_data.username).first():
        raise ValueError("用户名已存在")
    
    # 检查邮箱是否已存在
    if db.query(UserDB).filter(UserDB.email == user_data.email).first():
        raise ValueError("邮箱已存在")
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    db_user = UserDB(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username_or_email: str, password: str) -> Optional[UserDB]:
    """验证用户登录"""
    # 尝试通过用户名或邮箱查找用户
    user = db.query(UserDB).filter(
        (UserDB.username == username_or_email) | (UserDB.email == username_or_email)
    ).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user

def create_user_token(user: UserDB, remember_me: bool = False) -> str:
    """为用户创建访问令牌"""
    expires_delta = timedelta(minutes=1440 * 7) if remember_me else None
    token_data = {"sub": user.user_id}
    return create_access_token(token_data, expires_delta)

