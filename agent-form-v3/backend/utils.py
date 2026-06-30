"""
工具函数模块
"""
import re
import time
from pathlib import PurePosixPath


def sanitize_filename(filename: str) -> str:
    """清理文件名中的危险字符，防止路径遍历等攻击"""
    # 去掉路径部分（兼容 Linux/Windows 路径分隔符）
    name = PurePosixPath(filename).name
    name = name.split("\\")[-1]
    # 只保留安全字符：字母、数字、中文、下划线、连字符、点
    name = re.sub(r'[^\w\u4e00-\u9fff.\-]', '_', name)
    # 去掉开头的点（防止生成隐藏文件）
    name = name.lstrip('.')
    return name if name else "unnamed_file"


def sanitize_dirname(name: str) -> str:
    """清理目录名中的危险字符"""
    return re.sub(r'[^\w\u4e00-\u9fff\-]', '_', name)


def retry(max_retries: int = 3, base_delay: float = 1.0, retry_on: tuple = (Exception,)):
    """
    重试装饰器，支持指数退避。

    参数:
        max_retries: 最大重试次数（不含首次调用）
        base_delay: 首次重试等待秒数，后续翻倍
        retry_on: 需要重试的异常类型元组
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait = base_delay * (2 ** attempt)
                        print(f"  ⚠️ {func.__name__} 第{attempt+1}次失败，{wait:.0f}秒后重试: {e}")
                        time.sleep(wait)
            raise last_exception
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator

