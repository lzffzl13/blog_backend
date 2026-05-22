import logging
import sys


def setup_logging() -> None:
    """配置全局日志格式与级别"""
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # 根logger设置INFO级别，所有模块日志都会被捕获
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 避免重复添加handler
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # 降低第三方库日志级别，减少日志噪音
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
