from typing import Any, Optional

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

class ResponseCode:
    """响应状态码"""
    SUCCESS = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500


class ResponseMessage:
    """响应消息"""
    SUCCESS = "success"
    FAILED = "failed"
    BAD_REQUEST = "请求参数错误"
    UNAUTHORIZED = "未授权访问"
    FORBIDDEN = "禁止访问"
    NOT_FOUND = "资源不存在"
    INTERNAL_ERROR = "服务器内部错误"


def success_response(message: str = "success", data=None):
    content = {
        "code": 200,
        "message": message,
        "data": data
    }

    # 目标：把任何的 FastAPI、Pydantic、ORM 对象 都要正常响应 → code、message、data
    return JSONResponse(content=jsonable_encoder(content))

def error_response(
        message: str = ResponseMessage.FAILED,
        code: int = ResponseCode.BAD_REQUEST,
        data: Any = None
) -> dict:
    """
    错误响应

    Args:
        message: 错误消息
        code: 错误码
        data: 额外数据（可选）

    Returns:
        统一格式的错误响应字典
    """
    return {
        "code": code,
        "message": message,
        "data": data
    }


def paginated_response(
        data: Any,
        total: int,
        has_more: bool = False,
        message: str = ResponseMessage.SUCCESS,
        code: int = ResponseCode.SUCCESS
) -> dict:
    """
    分页响应

    Args:
        data: 数据列表
        total: 总记录数
        has_more: 是否有更多数据
        message: 响应消息
        code: 响应码

    Returns:
        统一格式的分页响应字典
    """
    return {
        "code": code,
        "message": message,
        "data": data,
        "total": total,
        "hasMore": has_more
    }

class APIResponse(JSONResponse):
    """
    自定义 API 响应类

    可用于需要自定义响应头的场景
    """

    def __init__(
            self,
            content: Any = None,
            status_code: int = 200,
            headers: Optional[dict] = None,
            media_type: str = "application/json"
    ):
        if isinstance(content, dict) and "code" not in content:
            content = success_response(data=content)
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type=media_type
        )
