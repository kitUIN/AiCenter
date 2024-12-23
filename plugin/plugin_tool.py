import json
import logging
from dataclasses import dataclass, field
from typing import Type, Literal

from rest_framework.request import Request
from rest_framework.response import Response

from center.models import TrainTask
from center.models.workflow import AiModelPower, TrainFile
from utils import ErrorResponse
from utils.jenkins import get_jenkins_manager

_plugin_templates = {}

logger = logging.getLogger(__name__)


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
    value: str | None = None
    """参数值"""
    info: str | None = None
    """说明"""
    allow_modify: bool = True
    """是否允许修改"""
    required: bool = False
    """是否必填"""


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


@dataclass
class ApiDocArgData:
    name: str
    """参数"""

    arg_type: str
    """参数类型"""

    children: list["ApiDocArgData"] = field(default_factory=list)
    """子参数"""

    required: bool = False
    """是否必须"""

    description: str = ""
    """描述"""


@dataclass
class ApiDocData:
    name: str
    """接口名称"""
    api: str
    """接口路径"""
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"]
    """请求内容类型"""
    content_type: Literal[
        "multipart/form-data", "application/x-www-form-urlencoded", "application/json", "application/xml",
        "text/plain", "application/octet-stream", "none"]
    """请求方法"""
    request_body: list[ApiDocArgData] = field(default_factory=list)
    """请求参数"""
    response_body: list[ApiDocArgData] = field(default_factory=list)
    """返回参数"""
    description: str = ""
    """描述"""
    request_example: str = ""
    """请求示例"""
    response_example: str = ""
    """返回示例"""


def get_predict_kwargs(args: str) -> dict:
    kwargs = {}
    if args:
        for arg in json.loads(args):
            if arg["type"] == "file":
                file_id = arg["value"].split("#")[-1]
                file = TrainFile.objects.filter(id=file_id).first()
                kwargs[arg["name"]] = file.file.path
            else:
                kwargs[arg["name"]] = arg["value"]
    return kwargs


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

    def get_power_args(self, *args, **kwargs) -> list[ArgData]:
        """配置参数"""
        return []

    def get_startup_args(self, *args, **kwargs) -> list[ArgData]:
        return []

    def get_plan(self, *args, **kwargs) -> dict:
        startup = self.get_startup(*args, **kwargs)
        _args = self.get_startup_args(*args, **kwargs)
        return {
            "startup": startup.__dict__,
            "args": [i.__dict__ for i in _args]
        }

    def predict(self, request: Request, text: str, image: list[PredictFile], power: AiModelPower) -> Response:
        kwargs = get_predict_kwargs(power.args)
        logger.info(f"能力#{power.id}({power.name})进行预测,参数:{kwargs}")
        if text:
            return self._predict_text(request, text, power, kwargs)
        elif image:
            return self._predict_image(request, image, power, kwargs)
        return ErrorResponse(msg="未开放")

    def _predict_text(self, request: Request, text: str, power: AiModelPower, kwargs: dict) -> Response:
        return ErrorResponse(msg="不支持文字预测")

    def _predict_image(self, request: Request, image: list[PredictFile], power: AiModelPower, kwargs: dict) -> Response:
        return ErrorResponse(msg="不支持图片预测")

    def callback_task_success(self, task: TrainTask):
        AiModelPower.objects.create(name=f"未命名能力{task.id}", task_id=task.id, key=self.key, args=[])
        get_jenkins_manager().download_task_artifacts(task)
        return None

    def get_api_doc(self, *args, **kwargs) -> ApiDocData:
        return ApiDocData(name="预测", method="POST", content_type="multipart/form-data", api="/predict", )

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
    "BasePlugin",
    "PredictFile",
    "ApiDocData",
    "ApiDocArgData",
]
