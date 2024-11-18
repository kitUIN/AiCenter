from django.db import models
from application.settings import TABLE_PREFIX
from center.models.ai import AIModel
from center.models.center_file import CenterFile
from center.models.dataset import DataSet
from utils import BaseModel


class TrainPlan(BaseModel):
    """训练计划"""
    name = models.CharField(max_length=64, unique=True, help_text="名称", verbose_name="名称", db_comment="名称")
    ai_model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name="plans", help_text="关联的模型",
                                 verbose_name="关联的模型", db_comment="关联的模型")

    class Meta:
        db_table = TABLE_PREFIX + "train_plan"
        verbose_name = '训练计划'
        verbose_name_plural = verbose_name


def train_directory_path(instance, filename):
    return f"train/ai_{instance.ai_model.id}/files/{filename}"


class TrainFile(CenterFile):
    """训练相关文件"""
    ai_model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name="files", help_text="关联的模型",
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
    plan = models.ForeignKey(TrainPlan, on_delete=models.CASCADE, related_name="tasks", help_text="使用的计划",
                             verbose_name="使用的计划", db_comment="使用的计划")
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE, related_name="tasks", help_text="使用的数据集",
                                verbose_name="使用的数据集", db_comment="使用的数据集")
    status = models.BooleanField(default=False, db_default=False, help_text="是否完成",
                                 verbose_name="是否完成", db_comment="是否完成")
    finished_datetime = models.DateTimeField(null=True, blank=True, help_text="完成时间", verbose_name="完成时间",
                                             db_comment="完成时间")

    class Meta:
        db_table = TABLE_PREFIX + "train_task"
        verbose_name = '训练任务'
        verbose_name_plural = verbose_name
