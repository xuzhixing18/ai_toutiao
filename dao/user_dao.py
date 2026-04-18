from datetime import timedelta, datetime

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from model.user import User, UserToken
from schema.user_vo import UserRequest, UserUpdateRequest, UserChangePasswordRequest
from common import security


# 根据用户名查询数据库
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


async def get_user_by_token(token: str, db: AsyncSession = None):
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    access_user = result.scalar_one_or_none()
    # 判断之前是否登录过 且 Token是否过期
    if not access_user or access_user.expire_time < datetime.now():
        return None

    query = select(User).where(User.id == access_user.user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def update_user_info(username: str, user_data: UserUpdateRequest, db: AsyncSession = None):
    sql = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_unset=True, exclude_none= True
    ))
    result = await db.execute(sql)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # 获取更新后的用户信息
    updated_user = get_user(db, username)
    return updated_user


async def update_user_pwd(pwd_data: UserChangePasswordRequest, cur_user: User, db = None):
    if not security.verify_password(pwd_data.old_password, cur_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="原密码错误")

    new_password = security.get_hash_password(pwd_data.new_password)
    sql = update(User).where(User.id == cur_user.id).values(password=new_password)
    result = await db.execute(sql)
    await db.commit()
    await db.refresh(cur_user)
    return result.rowcount > 0
