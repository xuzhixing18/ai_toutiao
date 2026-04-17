import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from api.v1 import news, user
from common.exception_handler import register_exception_handlers

# 配置基础日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 输出到控制台
    ]
)
app = FastAPI()

# 注册全局异常处理器
register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # 允许的源,生产环境需要配置具体地址
    allow_credentials=True, # 允许携带cookie
    allow_methods=["*"],    # 允许的请求方法
    allow_headers=["*"],    # 允许的请求头
)

app.include_router(news.router)
app.include_router(user.router)