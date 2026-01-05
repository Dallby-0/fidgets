from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import UserRegister, UserLogin, Token, User
from app.services.auth_service import register_user, authenticate_user, create_user_token
from app.dependencies import get_current_user
from app.db_models import UserDB

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    try:
        db_user = register_user(db, user_data)
        return {"message": "注册成功"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    user = authenticate_user(db, credentials.username_or_email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名/邮箱或密码错误",
        )
    
    access_token = create_user_token(user, credentials.remember_me)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": User(
            user_id=user.user_id,
            username=user.username,
            email=user.email
        )
    }

@router.get("/me", response_model=User)
def get_current_user_info(current_user: UserDB = Depends(get_current_user)):
    """获取当前用户信息"""
    return User(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email
    )

