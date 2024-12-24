import json
import logging

from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from dataclasses import field
from typing import Type, Literal

from rest_framework.request import Request
from rest_framework.response import Response

from center.models import TrainTask
from center.models.workflow import AiModelPower, TrainFile
from utils import ErrorResponse
from utils.jenkins import get_jenkins_manager

logger = logging.getLogger(__name__)


class ArgData(BaseModel):
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


class StartupData(BaseModel):
    value: str = ""
    """参数值"""
    allow_modify: bool = True
    """是否允许修改"""


class PlanTemplate(BaseModel):
    startup: StartupData
    """启动模板"""
    args: list[ArgData]
    """参数"""


class PredictFile(BaseModel):
    name: str
    """名称"""
    content: bytes
    """内容"""


class ApiDocArgData(BaseModel):
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


class ApiDocData(BaseModel):
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

    def get_plan_template(self, *args, **kwargs) -> PlanTemplate:
        return PlanTemplate(startup=self.get_startup(*args, **kwargs),
                            args=self.get_startup_args(*args, **kwargs))

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


__all__ = [
    "ArgData",
    "StartupData",
    "BasePlugin",
    "PredictFile",
    "ApiDocData",
    "ApiDocArgData",
    "PlanTemplate",
]
