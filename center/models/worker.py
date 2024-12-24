from django.db import models
import time

from application.settings import TABLE_PREFIX


class Worker(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    last_heartbeat = models.BigIntegerField(default=int(time.time()))
    status = models.CharField(max_length=32, default="unknown")

    def is_alive(self, timeout=10):
        """检查是否超时"""
        return (time.time() - self.last_heartbeat) <= timeout

    class Meta:
        db_table = TABLE_PREFIX + "worker"
        verbose_name = 'worker'
        verbose_name_plural = verbose_name
