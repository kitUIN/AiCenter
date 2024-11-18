from django.db import models

from application.settings import TABLE_PREFIX
from enums import FileStorageMethod
from utils import BaseModel


class CenterFile(BaseModel):
    """文件"""
    file_name = models.CharField(max_length=64, help_text="名称", verbose_name="名称", db_comment="名称")
    path = models.TextField(null=True, help_text="路径", verbose_name="路径", db_comment="路径")
    storage_method = models.IntegerField(default=0, db_default=0,   help_text="文件存储模式",
                                         verbose_name="文件存储模式", db_comment="文件存储模式")
    file = models.FileField(upload_to="files")

    class Meta:
        abstract = True
