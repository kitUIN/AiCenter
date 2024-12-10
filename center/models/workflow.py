from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, ModelSignal
from django.dispatch import receiver

from application.settings import TABLE_PREFIX
from center.models.ai import AIModel
from center.models.center_file import CenterFile
from center.models.dataset import DataSet
from enums import TrainTaskStatus
from utils import BaseModel
from utils.IntegerEnumField import IntegerEnumField
import json
from pathlib import Path


class TrainPlan(BaseModel):
    """训练计划"""
    name = models.CharField(max_length=64, unique=True, help_text="名称", verbose_name="名称", db_comment="名称")
    ai_model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name="plans", help_text="关联的模型",
                                 verbose_name="关联的模型", db_comment="关联的模型")
    startup = models.TextField(help_text="启动语句", verbose_name="启动语句", db_comment="启动语句")
    args = models.TextField(help_text="启动参数", verbose_name="启动参数", db_comment="启动参数")
    requirements = models.ForeignKey("TrainFile", null=True, on_delete=models.CASCADE, related_name="plans",
                                     help_text="环境文件", verbose_name="环境文件", db_comment="环境文件")

    def get_startup_cmd(self, result_folder: str):
        path = Path(result_folder)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        args = {i["name"]: i["value"] for i in json.loads(self.args)}
        args["result_folder"] = result_folder
        return self.startup.format(**args)

    class Meta:
        db_table = TABLE_PREFIX + "train_plan"
        verbose_name = '训练计划'
        verbose_name_plural = verbose_name


def train_directory_path(instance, filename: str):
    return f"{settings.MEDIA_ROOT}/train/ai_{instance.ai_model.id}/files/{filename}"


class TrainFile(CenterFile):
    """训练相关文件"""
    ai_model = models.ForeignKey(AIModel, null=True, on_delete=models.CASCADE, related_name="files",
                                 help_text="关联的模型",
                                 verbose_name="关联的模型", db_comment="关联的模型")

    file = models.FileField(upload_to=train_directory_path)

    class Meta:
        db_table = TABLE_PREFIX + "train_file"
        verbose_name = '训练相关文件'
        verbose_name_plural = verbose_name


class TrainConfigFile(CenterFile):
    """训练相关文件"""
    plan = models.ForeignKey(TrainPlan, on_delete=models.CASCADE, related_name="files", help_text="训练计划",
                             verbose_name="训练计划", db_comment="训练计划")
    file = models.FileField(upload_to="train/files/")

    class Meta:
        db_table = TABLE_PREFIX + "train_config_file"
        verbose_name = '训练相关文件'
        verbose_name_plural = verbose_name


class TrainTask(BaseModel):
    """训练任务"""
    ai_model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name="tasks", help_text="关联的模型",
                                 verbose_name="关联的模型", db_comment="关联的模型")
    plan = models.ForeignKey(TrainPlan, on_delete=models.CASCADE, related_name="tasks", help_text="使用的计划",
                             verbose_name="使用的计划", db_comment="使用的计划")
    #    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE, related_name="tasks", help_text="使用的数据集",
    #                                verbose_name="使用的数据集", db_comment="使用的数据集")
    number = models.IntegerField(db_default=0, default=0, help_text="构建次数",
                                 verbose_name="构建次数", db_comment="构建次数")
    status = IntegerEnumField(enum=TrainTaskStatus, default=TrainTaskStatus.Waiting, db_default=TrainTaskStatus.Waiting,
                              help_text="任务状态", verbose_name="任务状态", db_comment="任务状态")
    finished_datetime = models.DateTimeField(null=True, blank=True, help_text="完成时间", verbose_name="完成时间",
                                             db_comment="完成时间")

    class Meta:
        db_table = TABLE_PREFIX + "train_task"
        verbose_name = '训练任务'
        verbose_name_plural = verbose_name
        unique_together = (("plan", "number"),)
        ordering = ("-create_datetime",)


class TrainTaskStep(BaseModel):
    name = models.CharField(max_length=64, help_text="步骤名称", verbose_name="步骤名称", db_comment="步骤名称")

    task = models.ForeignKey("TrainTask", on_delete=models.CASCADE, related_name="steps")
    start_datetime = models.DateTimeField(null=True, help_text="任务步骤创建开始时间",
                                          verbose_name="任务步骤创建开始时间", db_comment="任务步骤创建开始时间")
    end_datetime = models.DateTimeField(null=True, help_text="任务步骤创建结束时间",
                                        verbose_name="任务步骤创建结束时间", db_comment="任务步骤创建结束时间")
    status = IntegerEnumField(enum=TrainTaskStatus, default=TrainTaskStatus.Waiting, db_default=TrainTaskStatus.Waiting,
                              help_text="任务步骤进行状态", verbose_name="任务步骤进行状态",
                              db_comment="任务步骤进行状态")

    class Meta:
        db_table = TABLE_PREFIX + "train_task_step"
        verbose_name = '训练任务日志'
        verbose_name_plural = verbose_name


class AiModelPower(BaseModel):
    name = models.CharField(max_length=64, help_text="名称", verbose_name="名称", db_comment="名称")
    task = models.ForeignKey("TrainTask", on_delete=models.CASCADE, related_name="powers")

    class Meta:
        db_table = TABLE_PREFIX + "ai_power"
        verbose_name = 'AI能力'
        verbose_name_plural = verbose_name


class AiModelPowerApiKey(BaseModel):
    id = models.CharField(max_length=128, primary_key=True, help_text="密钥", verbose_name="密钥", db_comment="密钥")
    power = models.ForeignKey("AiModelPower", on_delete=models.CASCADE, related_name="keys")
    status = models.BooleanField(default=True, db_default=True, )
    key = models.CharField(max_length=32, help_text="key", verbose_name="key", db_comment="key")

    class Meta:
        db_table = TABLE_PREFIX + "ai_power_key"
        verbose_name = 'AI能力'
        verbose_name_plural = verbose_name
