from django.db import models

from application.settings import TABLE_PREFIX
from utils import BaseModel


class AIModel(BaseModel):
    """AI模型"""
    name = models.CharField(max_length=64, unique=True, help_text="名称", verbose_name="名称", db_comment="名称")

    class Meta:
        db_table = TABLE_PREFIX + "ai_model"
        verbose_name = 'AI模型'
        verbose_name_plural = verbose_name
