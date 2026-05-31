from fastapi import HTTPException, status


class AppException(HTTPException):
    """应用基础异常"""

    def __init__(self, status_code: int, detail: str, error_code: str | None = None):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code


class NotFoundException(AppException):
    """资源不存在"""

    def __init__(self, detail: str = "资源不存在", error_code: str | None = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code or "NOT_FOUND",
        )


class ForbiddenException(AppException):
    """无权限访问"""

    def __init__(self, detail: str = "没有权限执行此操作", error_code: str | None = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code or "FORBIDDEN",
        )


class ConflictException(AppException):
    """资源冲突（如重复创建）"""

    def __init__(self, detail: str = "资源已存在", error_code: str | None = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code or "CONFLICT",
        )


class UnauthorizedException(AppException):
    """未认证"""

    def __init__(self, detail: str = "未认证", error_code: str | None = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code or "UNAUTHORIZED",
        )


class BadRequestException(AppException):
    """请求参数错误"""

    def __init__(self, detail: str = "请求参数错误", error_code: str | None = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code or "BAD_REQUEST",
        )
