from dataclasses import dataclass
from typing import Any, Type, Literal

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

    def get_plan(self, *args, **kwargs) -> dict:
        startup = self.get_startup(*args, **kwargs)
        _args = self.get_args(*args, **kwargs)
        return {
            "startup": startup.__dict__,
            "args": [i.__dict__ for i in _args]
        }

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
    "BasePlugin"
]
