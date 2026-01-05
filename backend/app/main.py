from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import auth, tasks, files, chat

app = FastAPI(title="模型微调云服务平台", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应设置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
@app.on_event("startup")
def on_startup():
    init_db()

# 注册路由
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(files.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": "模型微调云服务平台 API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

