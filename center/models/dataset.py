from concurrency.fields import IntegerVersionField

from application.settings import TABLE_PREFIX
from utils import BaseModel

from django.db import models


class DataSet(BaseModel):
    name = models.CharField(max_length=64, help_text="名称", verbose_name="名称", db_comment="名称")
    description = models.TextField(null=True, blank=True, help_text="描述信息", verbose_name="描述信息",
                                   db_comment="描述信息")
    status = models.BooleanField(default=False, db_default=False, help_text="是否标注完成",
                                 verbose_name="是否标注完成", db_comment="是否标注完成")

    task_number = models.IntegerField(default=0, db_default=0, help_text="总任务数量",
                                      verbose_name="总任务数量", db_comment="总任务数量")
    finished_task_number = models.IntegerField(default=0, db_default=0, help_text="完成任务数量",
                                               verbose_name="完成任务数量", db_comment="完成任务数量")
    total_predictions_number = models.IntegerField(default=0, db_default=0, help_text="总预测数量",
                                                   verbose_name="总预测数量", db_comment="总预测数量")
    total_annotations_number = models.IntegerField(default=0, db_default=0, help_text="总注解数量",
                                                   verbose_name="总注解数量", db_comment="总注解数量")
    skipped_annotations_number = models.IntegerField(default=0, db_default=0, help_text="跳过注解数量",
                                                     verbose_name="跳过注解数量", db_comment="跳过注解数量")
    ver = IntegerVersionField()

    class Meta:
        db_table = TABLE_PREFIX + "dataset"
        verbose_name = '数据集'
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)
