from dataclasses import dataclass
from typing import Any, Type, Literal
from rest_framework.response import Response

from utils import ErrorResponse

_plugin_templates = {}


def plugin_template(cls):
    _plugin_templates[cls._key] = cls
    return cls


@dataclass
class ArgData:
    id: int
    """id"""
    name: str
    """参数名称"""
    type: Literal["string", "file"] = "string"
    """参数类型"""
    value: str = ""
    """参数值"""
    info: str | None = None
    """说明"""
    allow_modify: bool = True
    """是否允许修改"""


@dataclass
class StartupData:
    value: str = ""
    """参数值"""
    allow_modify: bool = True
    """是否允许修改"""


@dataclass
class TaskStepData:
    name: str
    """名称"""
    cmd: str
    """执行命令"""
    step_type: Literal["normal", "venv"]
    """类型"""


@dataclass
class PredictFile:
    name: str
    """名称"""
    content: bytes
    """内容"""


class BasePlugin:
    _key: str = "base"
    _info: str = "默认说明"
    """说明"""
    _icon: str | None = None
    """图标"""

    def __init__(self):
        pass

    def get_startup(self, *args, **kwargs) -> StartupData:
        """返回启动命令"""
        return StartupData()

    def get_args(self, *args, **kwargs) -> list[ArgData]:
        """返回参数"""
        return []

    def get_task_steps(self, *args, **kwargs) -> list[TaskStepData]:
        """返回训练步骤"""
        return []

    def get_plan(self, *args, **kwargs) -> dict:
        startup = self.get_startup(*args, **kwargs)
        _args = self.get_args(*args, **kwargs)
        return {
            "startup": startup.__dict__,
            "args": [i.__dict__ for i in _args]
        }

    def predict(self, text: str, image: list[PredictFile]) -> Response:
        if text:
            return self._predict_text(text)
        elif image:
            return self._predict_image(image)
        return ErrorResponse(msg="未开放")

    def _predict_text(self, text: str) -> Response:
        return ErrorResponse(msg="不支持文字预测")

    def _predict_image(self, image: list[PredictFile]) -> Response:
        return ErrorResponse(msg="不支持图片预测")

    @property
    def key(self):
        return self._key

    @property
    def info(self):
        return self.info

    @property
    def icon(self):
        return self.icon


def get_plugin_templates() -> dict[str, Type[BasePlugin]]:
    return _plugin_templates


__all__ = [
    "get_plugin_templates",
    "plugin_template",
    "ArgData",
    "StartupData",
    "TaskStepData",
    "BasePlugin"
]
