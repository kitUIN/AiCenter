import logging
import os
import subprocess
import sys
import time
from datetime import datetime

from celery.app import shared_task

from center.models.workflow import  TrainTask
from enums import TrainTaskStatus
import pytz

logger = logging.getLogger(__name__)


def create_venv(env_name: str):
    logger.info(f"开始创建虚拟环境{env_name}")
    process = subprocess.Popen([sys.executable, "-m", "venv", env_name],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, )
    process.wait()
    logger.info(f"创建虚拟环境{env_name}结束")
    return True


def install_package(env_name, requirements):
    if requirements is None:
        logger.info(f"{env_name}无依赖跳过")
        return True
    logger.info(f"{env_name}开始安装依赖")
    pip_executable = os.path.join(env_name, "bin", "pip") if os.name != "nt" else os.path.join(env_name, "Scripts",
                                                                                               "pip.exe")
    process = subprocess.Popen([pip_executable, "install", "-r", requirements],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, )
    with open(f"{env_name}/requirements.out", "a+", encoding="utf8") as f:
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if line:
                logger.info(line)
                f.write(f"{datetime.now()} | {env_name} | {line}\n")
                f.flush()
    process.stdout.close()
    process.wait()
    return True


def get_now():
    return datetime.now(tz=pytz.timezone('UTC'))


@shared_task(ignore_result=True, routing_key='train', exchange='train')
def start_train(task_id: int):
    task = TrainTask.objects.get(id=task_id)
    task.status = TrainTaskStatus.Running
    task.save()
    task.log.venv = TrainTaskStatus.Running
    task.log.venv_start_datetime = get_now()
    task.log.save()
    venv_name = f"train_task/{task.plan.name}_{task.id}"
    try:
        create_venv(venv_name)
        task.log.venv = TrainTaskStatus.Succeed
        task.log.venv_end_datetime = get_now()
        task.log.save()
    except Exception as e:
        logger.exception(e)
        task.log.venv = TrainTaskStatus.Fail
        task.log.venv_end_datetime = get_now()
        task.log.save()
        task.status = TrainTaskStatus.Fail
        task.save()
        return False
    task.log.requirements = TrainTaskStatus.Running
    task.log.requirements_start_datetime = get_now()
    task.log.save()
    try:
        install_package(venv_name, task.plan.requirements.file if task.plan.requirements else None)
        task.log.requirements = TrainTaskStatus.Succeed
        task.log.requirements_end_datetime = get_now()
        task.log.save()
    except Exception as e:
        logger.exception(e)
        task.log.requirements = TrainTaskStatus.Fail
        task.log.requirements_end_datetime = get_now()
        task.log.save()
        task.status = TrainTaskStatus.Fail
        task.save()
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


if __name__ == '__main__':
    create_venv("train")
    install_package("train", "requirements.txt")
