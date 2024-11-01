from django.db import models


class BaseModel(models.Model):
    """
    核心标准抽象模型模型,可直接继承使用
    """
    id = models.BigAutoField(primary_key=True, help_text="Id", verbose_name="Id")
    update_datetime = models.DateTimeField(auto_now=True, null=True, blank=True, help_text="修改时间",
                                           verbose_name="修改时间", db_comment="修改时间")
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="创建时间",
                                           verbose_name="创建时间", db_comment="创建时间")

    class Meta:
        abstract = True
        verbose_name = '基础模型'
        verbose_name_plural = verbose_name
