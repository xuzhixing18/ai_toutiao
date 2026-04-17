from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

# 对象基础类
class BaseField(DeclarativeBase):
    # 创建时间
    create_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment='创建时间')
    update_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, comment='更新时间')