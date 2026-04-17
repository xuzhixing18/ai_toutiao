from datetime import datetime

from sqlalchemy import DateTime, String, Integer, Text, Index
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

from model.base import BaseField

class Category(BaseField):
    __tablename__ = 'news_category'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment='分类id')  # 主键自增
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment='分类名称')   # 唯一非空约束
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment='排序')

    def __repr__(self):
        return f'<Category: id= {self.id}, name = {self.name}, sort_order = {self.sort_order}>'


class News(BaseField):
    __tablename__ = 'news'

    __table_args__ = (
        Index('news_category_idx', 'category_id'),  # 创建分类id的索引
        Index('publish_time_idx', 'publish_time')   # 创建发布时间的索引
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False, comment='新闻ID')  # 主键自增
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment='新闻标题')   # 唯一非空约束
    description: Mapped[str] = mapped_column(String(500), comment='新闻简介')
    content: Mapped[str] = mapped_column(Text, nullable=False, comment='新闻内容')
    image: Mapped[str] = mapped_column(String(255), comment='封面图片URL')
    author: Mapped[str] = mapped_column(String(50), comment='作者')
    category_id: Mapped[int] = mapped_column(Integer, comment='分类ID')
    views: Mapped[int] = mapped_column(Integer, comment='浏览量')
    publish_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, comment='发布时间')

    def __repr__(self):
        return f'<News: id= {self.id}, title = {self.title}, description= {self.description}, image = {self.image}, author = {self.author}, category_id = {self.category_id}>'