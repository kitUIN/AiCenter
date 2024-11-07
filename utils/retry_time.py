import logging
import time
from functools import wraps

import requests
from concurrency.exceptions import RecordModifiedError
from django.db import IntegrityError
from redis import WatchError

RetryMaxCount = 250

logger = logging.getLogger(__name__)


class RetryException(Exception):
    pass


def retry_create(max_count: int = 2, default=None):
    """重试

    仅抛出 C{RetryException} 与 C{ReadTimeout} 时进行重试

    @param max_count: 最大可重试次数
    @param default: 超出重试次数后默认返回
    """

    def _task_retry(task_func):
        @wraps(task_func)
        def wrapper(*args, **kwargs):
            for i in range(max_count + 1):
                try:
                    task_result = task_func(*args, **kwargs)
                    return task_result
                except RetryException:
                    pass
                except requests.exceptions.ReadTimeout:
                    pass
            return default

        return wrapper

    return _task_retry


def retry_save(time_interval: int = 0):
    """
    任务重试装饰器
    Args:
        time_interval: 每次重试间隔
    """

    def _task_retry(task_func):
        @wraps(task_func)
        def wrapper(*args, **kwargs):
            while True:
                try:
                    task_result = task_func(*args, **kwargs)
                    return task_result
                except RecordModifiedError:
                    if time_interval > 0:
                        time.sleep(time_interval)
                except IntegrityError as e:
                    logger.error(e)
                    if time_interval > 0:
                        time.sleep(time_interval)
                except WatchError:
                    if time_interval > 0:
                        time.sleep(time_interval)

        return wrapper

    return _task_retry


def retry_normal(max_count: int = 3, default_res=None):
    def _task_retry(task_func):
        @wraps(task_func)
        def wrapper(*args, **kwargs):
            for i in range(max_count):
                try:
                    task_result = task_func(*args, **kwargs)
                    return task_result
                except Exception as e:
                    if not isinstance(e, Exception):
                        logger.exception(e)

            return default_res

        return wrapper

    return _task_retry
# def retry_redis_save():
#     conn: Redis = get_redis_connection("default")
#     pipe = conn.pipeline()
#
#     while 1:
#         try:
#             pipe.watch(KEY)  # 监听库存
#             c = int(pipe.get(KEY))  # 查看当前库存
#             if c > 0:  # 有库存则售卖
#                 pipe.multi()  # 开始事务
#                 c -= 1
#                 pipe.set(KEY, c)  # 减少库存
#                 pipe.execute()  # 执行事务
#                 # 抢购成功并结束
#                 print('用户 {} 抢购成功，商品剩余 {}'.format(i, c))
#                 break
#             else:
#                 # 库存卖完，抢购结束
#                 print('用户 {} 抢购停止，商品卖完'.format(i))
#                 break
#         except Exception as e:
#             # 抢购失败，重试
#             print('用户 {} 抢购失败，重试一次'.format(i))
#             continue
#         finally:
#             # 重置 pipe，准备下次抢购
#             pipe.reset()
