from datetime import timedelta, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from model.user import User, UserToken
from schema.user_vo import UserRequest
from common import security


# 根据用户名查询数据库
# async def get_user(username: str, db: AsyncSession = None):
async def get_user(db: AsyncSession, username: str):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()


# 新增用户
async def create_user(db: AsyncSession, user_request: UserRequest):
    hash_password = security.get_hash_password(user_request.password)
    user = User(username=user_request.username, password=hash_password)
    db.add(user)
    await db.commit()
    # 返回数据库中最新的User数据
    await db.refresh(user)
    return user



async def create_token(db: AsyncSession, user_id: int):
    token_prefix = "toutiao_access_token"
    # Token有效期设置为7天
    expire_delta = timedelta(days=7)
    expire_time = datetime.now() + expire_delta

    token = security.create_access_token(token_prefix + str(user_id), expire_delta)

    query = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(query)
    access_user = result.scalar_one_or_none()

    if access_user:
        access_user.token = token
        access_user.expire_time = expire_time
    else:
        access_user = UserToken(user_id=user_id, token=token, expire_time=expire_time)
        db.add(access_user)
        await db.commit()
    return token


async def authenticate_user(user_request: UserRequest, db: AsyncSession = None):
    user = await get_user(db, user_request.username)
    # 校验查询出的密码和用户输入的密码经由哈希计算后 是否相同
    if user and security.verify_password(user_request.password, user.password):
        return user
    return None