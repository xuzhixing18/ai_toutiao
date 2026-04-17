from datetime import datetime
from typing import Optional

from model.base import BaseField
from sqlalchemy import DateTime, String, Integer, Index, Enum
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class User(BaseField):
    __tablename__='user'

    __table_args__ = (
        Index('uname_unique_idx','username'),
        Index('phone_unique_idx','phone')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False,comment="用户ID")
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名")
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码")
    nickname: Mapped[Optional[str]] = mapped_column(String(50), comment="用户昵称")
    avatar: Mapped[Optional[str]] = mapped_column(String(255), comment="头像URL", default='https://fastly.jsdelivr.net/npm/@vant/assets@1.0.8/sand.jpeg')
    gender: Mapped[Optional[int]] = mapped_column(Enum('male','female','unknown'),comment="性别",default="unknown")
    bio: Mapped[Optional[str]] = mapped_column(String(500), comment="个人简介", default="这个人很懒,什么都没留下")
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, comment="手机号")


class Base(DeclarativeBase):
    pass

class UserToken(Base):
    __tablename__ = 'user_token'

    __table_args__ = (
        Index('user_id_idx','user_id'),
        Index('token_idx','token'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False, comment="令牌ID")
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="用户ID")
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, comment="登录令牌")
    expire_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="令牌过期时间")
    create_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(), comment="创建时间")


    def __repr__(self):
        return f"<UserToken(id={self.id}, user_id={self.user_id}, token={self.token}, expire_time={self.expire_time})>"
        return f"<UserToken(id={self.id}, user_id={self.user_id}, token={self.token}, expire_time={self.expire_time})>"