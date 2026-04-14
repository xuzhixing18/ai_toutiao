from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# 数据库url
async_db_url = "mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8"

# 接口实现流程:
# 1.模块化路由 => API接口规范文档
# 2.定义模型类 => 数据库表(需遵循)

# 创建异步引擎
async_engine = create_async_engine(
    async_db_url,
    echo=True,       # 输出SQL日志
    pool_size=10,    # 设置连接池中保持的持久连接数
    max_overflow=20, # 设置连接池允许创建的额外连接数
    future=True,   # 兼容sqlalchemy2.0
)

# 创建异步会话工厂
local_async_session = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 依赖项,用于获取数据库会话
async def get_db():
    async with local_async_session() as session:
        try:
            yield session
            # 当前会话的所有操作执行完毕才会提交
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()