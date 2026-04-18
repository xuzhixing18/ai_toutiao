from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from common.auth import get_current_user
from common.response import success_response
from config.db_conf import get_db
from model.user import User
from schema.user_vo import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest, UserChangePasswordRequest
from dao import user_dao

router = APIRouter(prefix="/api/user", tags=["user"])

# 用户注册
@router.post("/register")
async def register(user_request: UserRequest, db: AsyncSession = Depends(get_db)):
    db_user = await user_dao.get_user(db, user_request.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="用户已存在")

    register_user = await user_dao.create_user(db, user_request)
    token = await user_dao.create_token(db, register_user.id)
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(register_user))
    return success_response(message="注册成功", data=response_data)



# 用户登录
@router.post("/login")
async def login(user_request: UserRequest, db: AsyncSession = Depends(get_db)):
    db_user = await user_dao.authenticate_user(user_request, db)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = await user_dao.create_token(db, db_user.id)
    response_data = UserAuthResponse(token=token, user_info=UserInfoResponse.model_validate(db_user))
    return success_response(message="登录成功啦", data=response_data)


@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    return success_response(message="获取用户信息成功", data=UserInfoResponse.model_validate(user))


# 修改用户信息
@router.put("/update")
async def update_user_info(user_data: UserUpdateRequest,
                           cur_user: User = Depends(get_current_user),
                           db: AsyncSession = Depends(get_db)):
    db_user = await user_dao.update_user_info(cur_user.username, user_data, db)
    return success_response(message="更新用户信息成功", data=UserInfoResponse.model_validate(db_user))


@router.put("/password")
async def update_user_pwd(pwd_data: UserChangePasswordRequest,
                          cur_user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    update_user_res = await user_dao.update_user_pwd(pwd_data, cur_user, db)
    if not update_user_res:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="密码修改失败")
    return success_response(message="修改密码成功")
