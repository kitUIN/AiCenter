from enum import Enum


class TrainTaskStatus(Enum):
    """训练任务状态"""
    Waiting = 0
    """等待中"""
    Running = 1
    """运行中"""
    Canceled = 2
    """已取消"""
    Succeed = 3
    """成功"""

