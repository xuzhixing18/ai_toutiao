from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from dao import news_dao
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/news", tags=["news"])

@router.get("/category")
async def get_category(offset: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    db_category = await news_dao.get_categories(db, offset, limit)
    return {
        "code": 200,
        "message": "success",
        "data": db_category,
    }

# 根据分类id 分页查询对应的新闻列表
# /api/news/list?categoryId=8&page=4&pageSize=15
@router.get("/list")
async def get_list(category_id: int = Query(..., alias="categoryId"),   # alias: 给请求url中的参数映起别名
                   page: int = 1,
                   page_size: int = Query(10, alias="pageSize", le=100),
                   db: AsyncSession = Depends(get_db)):
    offset = (page - 1) * page_size
    news_list = await news_dao.get_list_by_category_id(category_id, offset, page_size, db)
    total = await news_dao.list_count(category_id, db)
    # 是否还有更多记录可以加载
    hasMore = offset + len(news_list) < total
    return {
        "code": 200,
        "message": "success",
        "data": news_list,
        "total": total,
        "hasMore": hasMore
    }

# 查询当前新闻详情 + 浏览量加1 + 查询当前新闻的关联新闻(同分类下的其他新闻)
@router.get("/detail")
async def get_detail(id: int, db: AsyncSession = Depends(get_db)):
    news_detail = await news_dao.get_detail(id, db)
    if not news_detail:
        raise HTTPException(status_code=404, detail="当前新闻不存在")

    views = await news_dao.increase_news_views(id, db)
    # 为保证可用性,只是记录日志
    if not views:
        logger.error(f"当前新闻: {id} 浏览量加1失败")

    # 获取当前新闻的关联新闻/推荐
    related_news = await news_dao.get_related_news(news_detail.category_id, id, 5, db)

    return {
      "code": 200,
      "message": "success",
      "data": {
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views,
        "relatedNews": related_news
      }
    }