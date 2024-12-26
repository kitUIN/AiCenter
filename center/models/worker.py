import logging

from django.db import models
import time
import requests
from application.settings import TABLE_PREFIX

logger = logging.getLogger(__name__)


class Worker(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    last_heartbeat = models.BigIntegerField(default=int(time.time()))
    status = models.CharField(max_length=32, default="unknown")
    url = models.CharField(max_length=256, null=True)
    name = models.CharField(max_length=64, null=True)

    def request(self, method, api, data=None, json=None, files=None):
        res = requests.request(method, self.url + api, data=data, json=json, files=files)
        logger.info(f"{api} - {method} - {res.status_code}: {res.text}")
        if res.status_code == 200:
            resp = res.json()
            return resp
        return None

    def get_plan_template(self):
        api = "/plugin/plan/template"
        return self.request("GET", api)

    def get_api_doc(self):
        api = "/plugin/api/doc"
        return self.request("GET", api)

    def get_power_args(self, json):
        api = "/plugin/power/args"
        return self.request("POST", api, json=json)

    def predict(self, files, data):
        api = "/plugin/predict"
        return self.request("POST", api, files=files, data=data)

    def callback_build_success(self, data):
        api = "/plugin/build/success"
        return self.request("POST", api, json=data)

    @staticmethod
    def is_active(key, timeout=10):
        return Worker.objects.filter(id=key, last_heartbeat__lte=int(time.time()) + timeout).exists()

    @staticmethod
    def active_all(timeout=10):
        return Worker.objects.filter(last_heartbeat__lte=int(time.time()) + timeout)

    def is_alive(self, timeout=10):
        """检查是否超时"""
        return (time.time() - self.last_heartbeat) <= timeout

    class Meta:
        db_table = TABLE_PREFIX + "worker"
        verbose_name = 'worker'
        verbose_name_plural = verbose_name
