from django.db import models

from application.settings import TABLE_PREFIX
from enums import FileStorageMethod
from utils import BaseModel


class CenterFile(BaseModel):
    """文件"""
    file_name = models.CharField(max_length=64, help_text="名称", verbose_name="名称", db_comment="名称")
    path = models.TextField(help_text="路径", verbose_name="路径", db_comment="路径")
    storage_method = models.IntegerField(default=0, db_default=0, choices=FileStorageMethod, help_text="文件存储模式",
                                         verbose_name="文件存储模式", db_comment="文件存储模式")

    class Meta:
        db_table = TABLE_PREFIX + "center_file"
        verbose_name = '文件'
        verbose_name_plural = verbose_name
