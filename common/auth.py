from fastapi import Header, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from dao import user_dao


async def get_current_user(
        authorization: str = Header( ..., alias="Authorization"),
        db: AsyncSession = Depends(get_db)
):
    # token = authorization.split(" ")[1]
    token = authorization.replace("Bearer ", "")
    cur_user = await user_dao.get_user_by_token(token, db)
    if not cur_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌无效或已过期,请重新登录")
    return cur_user

