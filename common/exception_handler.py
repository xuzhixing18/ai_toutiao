import logging

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, OperationalError
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException

from common.response import error_response, ResponseCode, ResponseMessage

logger = logging.getLogger(__name__)

def register_exception_handlers(app: FastAPI):
    """
    注册全局异常处理器

    Args:
        app: FastAPI 应用实例
    """

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        处理 HTTP 异常

        捕获所有 HTTPException，返回统一格式的错误响应
        """
        logger.warning(
            f"HTTP异常 - 路径: {request.url.path}, "
            f"状态码: {exc.status_code}, "
            f"详情: {exc.detail}"
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(
                message=exc.detail if isinstance(exc.detail, str) else ResponseMessage.FAILED,
                code=exc.status_code
            )
        )

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
        """
        处理 Starlette HTTP 异常
        """
        logger.warning(
            f"Starlette HTTP异常 - 路径: {request.url.path}, "
            f"状态码: {exc.status_code}, "
            f"详情: {exc.detail}"
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(
                message=str(exc.detail) if exc.detail else ResponseMessage.FAILED,
                code=exc.status_code
            )
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        处理请求参数验证异常

        当请求参数不符合 Pydantic 模型定义时触发
        """
        logger.warning(
            f"参数验证失败 - 路径: {request.url.path}, "
            f"错误: {exc.errors()}"
        )

        # 提取更友好的错误信息
        errors = []
        for error in exc.errors():
            field = ".".join(str(x) for x in error.get("loc", []))
            message = error.get("msg", "参数错误")
            errors.append(f"{field}: {message}")

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(
                message="; ".join(errors),
                code=ResponseCode.BAD_REQUEST,
                data={"details": exc.errors()}
            )
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        """
        处理 Pydantic 验证异常
        """
        logger.warning(
            f"Pydantic验证失败 - 路径: {request.url.path}, "
            f"错误: {exc.errors()}"
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(
                message="数据验证失败",
                code=ResponseCode.BAD_REQUEST,
                data={"details": exc.errors()}
            )
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """
        处理数据库完整性约束异常

        例如：唯一约束冲突、外键约束等
        """
        logger.error(
            f"数据库完整性错误 - 路径: {request.url.path}, "
            f"错误: {str(exc.orig)}"
        )

        # 判断是否是唯一约束冲突
        error_msg = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
        if 'Duplicate entry' in error_msg or 'UNIQUE constraint' in error_msg:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=error_response(
                    message="数据已存在",
                    code=ResponseCode.BAD_REQUEST
                )
            )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response(
                message="数据完整性错误",
                code=ResponseCode.BAD_REQUEST,
                data={"detail": error_msg}
            )
        )

    @app.exception_handler(OperationalError)
    async def operational_error_handler(request: Request, exc: OperationalError):
        """
        处理数据库操作异常

        例如：连接失败、数据类型错误等
        """
        logger.error(
            f"数据库操作错误 - 路径: {request.url.path}, "
            f"错误: {str(exc.orig)}"
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(
                message="数据库操作失败，请稍后重试",
                code=ResponseCode.INTERNAL_ERROR
            )
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        处理所有未捕获的通用异常

        这是最后的防线，确保任何异常都能返回统一格式
        """
        logger.error(
            f"未捕获的异常 - 路径: {request.url.path}, "
            f"类型: {type(exc).__name__}, "
            f"错误: {str(exc)}",
            exc_info=True  # 记录完整的堆栈跟踪
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(
                message="服务器内部错误，请联系管理员",
                code=ResponseCode.INTERNAL_ERROR
            )
        )

    logger.info("全局异常处理器注册成功")
