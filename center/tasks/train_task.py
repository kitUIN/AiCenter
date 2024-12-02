import logging
import os
import subprocess
import sys
import time
from datetime import datetime

from celery.app import shared_task

from center.models.workflow import TrainTask, TrainTaskLog
from enums import TrainTaskStatus
import pytz
from pathlib import Path

logger = logging.getLogger(__name__)


def get_now():
    return datetime.now(tz=pytz.timezone('UTC'))


class TrainTaskManager:
    def __init__(self, env_name: str, task_id: int, task_log_id: int):
        self.task_id = task_id
        self.task_log_id = task_log_id
        self.env_name = Path(env_name)
        self.venv_path = Path(env_name).joinpath("venv")

    def _create_venv(self):
        logger.info(f"开始创建虚拟环境{self.venv_path}")
        process = subprocess.Popen([sys.executable, "-m", "venv", self.venv_path],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, )
        process.wait()
        logger.info(f"创建虚拟环境{self.venv_path}结束")
        return True

    def create_venv(self):
        """安装虚拟环境"""
        try:
            self._create_venv()
            TrainTaskLog.objects.filter(id=self.task_log_id).update(
                venv=TrainTaskStatus.Succeed, venv_end_datetime=get_now()
            )
            return True
        except Exception as e:
            logger.exception(e)
            _now = get_now()
            TrainTaskLog.objects.filter(id=self.task_log_id).update(
                venv=TrainTaskStatus.Fail, venv_end_datetime=_now
            )
            TrainTask.objects.filter(id=self.task_id).update(status=TrainTaskStatus.Fail, update_datetime=_now)
            return False

    def _install_package(self, requirements: str | None, ):
        if requirements is None:
            logger.info(f"{self.env_name}无依赖跳过")
            return True
        logger.info(f"{self.env_name}开始安装依赖")
        pip_executable = self.venv_path.joinpath("bin", "pip") if os.name != "nt" else self.venv_path.joinpath(
            "Scripts",
            "pip.exe")
        process = subprocess.Popen([pip_executable, "install", "-r", requirements],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, )
        c = 0
        with open(f"{self.env_name}/requirements.out", "a+", encoding="utf8") as f:
            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                if line:
                    c += 1
                    f.write(f"{datetime.now()} | {line}\n")
                    f.flush()
                    if c >= 10:
                        c = 0
                        if TrainTask.objects.filter(id=self.task_id, status=TrainTaskStatus.Canceled).exists():
                            process.kill()
                            return False
        process.stdout.close()
        process.wait()
        return True

    def install_package(self, requirements: str | None, ):
        """安装依赖"""
        if TrainTask.objects.filter(id=self.task_id, status=TrainTaskStatus.Canceled).exists():
            return False
        TrainTaskLog.objects.filter(id=self.task_log_id).update(
            requirements=TrainTaskStatus.Running, requirements_start_datetime=get_now()
        )
        try:
            self._install_package(requirements=requirements)
            TrainTaskLog.objects.filter(id=self.task_log_id).update(
                requirements=TrainTaskStatus.Succeed, requirements_end_datetime=get_now()
            )
            return True
        except Exception as e:
            logger.exception(e)
            _now = get_now()
            TrainTaskLog.objects.filter(id=self.task_log_id).update(
                requirements=TrainTaskStatus.Fail, requirements_end_datetime=_now
            )
            TrainTask.objects.filter(id=self.task_id).update(status=TrainTaskStatus.Fail, update_datetime=_now)
            return False

    def _start_train(self):
        pass

    def start_train(self):
        if TrainTask.objects.filter(id=self.task_id, status=TrainTaskStatus.Canceled).exists():
            return False
        TrainTaskLog.objects.filter(id=self.task_log_id).update(
            train=TrainTaskStatus.Running, train_start_datetime=get_now()
        )
        try:
            self._start_train()
            _now = get_now()
            TrainTaskLog.objects.filter(id=self.task_log_id).update(
                train=TrainTaskStatus.Succeed, train_end_datetime=_now
            )
            TrainTask.objects.filter(id=self.task_id).update(status=TrainTaskStatus.Succeed, finished_datetime=_now,
                                                             update_datetime=_now)
            return True
        except Exception as e:
            logger.exception(e)
            _now = get_now()
            TrainTaskLog.objects.filter(id=self.task_log_id).update(
                train=TrainTaskStatus.Fail, train_end_datetime=_now
            )
            TrainTask.objects.filter(id=self.task_id).update(status=TrainTaskStatus.Fail, update_datetime=_now)
            return False


@shared_task(ignore_result=True, routing_key='train', exchange='train')
def start_train(task_id: int):
    task = TrainTask.objects.get(id=task_id)
    task.status = TrainTaskStatus.Running
    task.save()
    TrainTaskLog.objects.filter(id=task.log.id).update(
        venv=TrainTaskStatus.Running, venv_start_datetime=get_now()
    )
    venv_name = f"train_task/{task.plan.name}_{task.id}"
    manager = TrainTaskManager(venv_name, task.id, task.log.id)
    if not manager.create_venv():
        return False
    if not manager.install_package(task.plan.requirements.file.path if task.plan.requirements else None):
        return False
    if not manager.start_train():
        return False
    return True


def follow_file(file_path):
    """监听文件的新内容"""
    with open(file_path, 'r') as file:
        file.seek(0, 2)
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line
