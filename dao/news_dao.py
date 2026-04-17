from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Query

from model.news import Category, News

# 获取新闻分类
async def get_categories(db: AsyncSession, offset: int = 0, limit: int = 100):
    sql = select(Category).offset(offset).limit(limit)
    result = await db.execute(sql)
    return result.scalars().all()

# 根据分类id获取对应的新闻列表
async def get_list_by_category_id(
        category_id: int,
        offset: int = Query(1, description="跳过的记录数"),
        limit: int = Query(10, le=100, description="每页记录数"),
        db: AsyncSession = None):

    sql = select(News).where(News.category_id == category_id).offset(offset).limit(limit)
    result = await db.execute(sql)
    return result.scalars().all()

async def list_count(category_id: int, db: AsyncSession = None):
    sql = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(sql)
    return result.scalar()

# 根据分类id查询新闻详情
async def get_detail(id: int, db: AsyncSession = None):
    sql = select(News).where(News.id == id)
    news = await db.execute(sql)
    return news.scalar_one_or_none()


# 当前新闻的浏览量加1
async def increase_news_views(id: int, db: AsyncSession = None):
    sql = update(News).where(News.id == id).values(views=News.views + 1)
    result = await db.execute(sql)
    await db.commit()
    # 检查浏览量是否增加成功
    return result.rowcount > 0

# 根据分类id 查询当前新闻的关联新闻
async def get_related_news(category_id: int, id: int, limit: int = 5, db: AsyncSession = None):
    sql = select(News).where(
        # 查询同一分类的相关新闻
        News.id != id, News.category_id == category_id
        ).order_by(
            # 先按浏览量排序，再按时间排序
            News.views.desc(), News.publish_time.desc()
        ).limit(limit)
    result = await db.execute(sql)
    # return result.scalars().all()
    related_news = result.scalars().all()
    # 关联新闻只返回必要字段
    return [{
        "id": news.id,
        "title": news.title,
        "image": news.image,
        "author": news.author,
        "views": news.views,
    } for news in related_news]
