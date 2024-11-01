from application.settings import TABLE_PREFIX
from utils import BaseModel

from django.db import models


class DataSet(BaseModel):
    name = models.CharField(max_length=64, unique=True, help_text="名称", verbose_name="名称", db_comment="名称")

    status = models.BooleanField(default=False, db_default=False, help_text="是否标注完成",
                                 verbose_name="是否标注完成", db_comment="是否标注完成")

    class Meta:
        db_table = TABLE_PREFIX + "dataset"
        verbose_name = '数据集'
        verbose_name_plural = verbose_name
