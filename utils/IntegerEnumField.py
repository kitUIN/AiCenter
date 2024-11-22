from django.db import models
from enum import Enum


class IntegerEnumField(models.IntegerField):
    def __init__(self, enum, *args, **kwargs):
        """
        :param enum: 必须传递一个 Enum 类，用于限定字段值
        """
        if not issubclass(enum, Enum):
            raise TypeError("`enum` 参数必须是一个 Enum 子类")
        self.enum = enum
        kwargs['choices'] = [(e.value, e.name) for e in enum]
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        """
        支持字段的迁移
        """
        name, path, args, kwargs = super().deconstruct()
        kwargs['enum'] = self.enum
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection):
        """
        数据库中的整数值 -> Python 的 Enum 对象
        """
        if value is None:
            return value
        return self.enum(value)

    def to_python(self, value):
        """
        确保将值转换为 Enum 类型
        """
        if isinstance(value, self.enum):
            return value
        if value is None:
            return value
        return self.enum(value)

    def get_prep_value(self, value):
        """
        Enum 对象 -> 数据库存储的整数值
        """
        if isinstance(value, self.enum):
            return value.value
        if value is None:
            return value
        return int(value)
