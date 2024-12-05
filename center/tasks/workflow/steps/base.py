import logging
import subprocess
from datetime import datetime
from pathlib import Path

import pytz

from center.models.workflow import TrainTask, TrainTaskStep
from enums import TrainTaskStatus

logger = logging.getLogger(__name__)


def get_now():
    return datetime.now(tz=pytz.timezone('UTC'))


class BaseWorkflowStep:

    def __init__(self, name: str):
        self._name = name

    def run(self, env_name: Path, cmd: str, task_id: int, task_step_id: int, **kwargs):
        try:
            return self._run(env_name, cmd, task_id, task_step_id, **kwargs)
        except Exception as e:
            logger.exception(e)
            _now = get_now()
            TrainTaskStep.objects.filter(id=task_step_id).update(
                status=TrainTaskStatus.Fail, end_datetime=_now
            )
            TrainTask.objects.filter(id=task_id).update(status=TrainTaskStatus.Fail, update_datetime=_now)
            return False

    def _run(self, env_name: Path, cmd: str, task_id: int, task_step_id: int, **kwargs) -> bool:
        if self._check_cancel(task_id, task_step_id):
            return False
        TrainTaskStep.objects.filter(id=task_step_id).update(
            status=TrainTaskStatus.Running, start_datetime=get_now()
        )
        logs = env_name.joinpath("logs")
        if not logs.exists():
            logs.mkdir(parents=True, exist_ok=True)
        process = subprocess.Popen(cmd, shell=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, )
        c = 0

        with logs.joinpath(f"{task_step_id}.out").open("a+", encoding="utf8") as f:
            f.write(f"{datetime.now()} | {cmd}\n")
            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                if line:
                    c += 1
                    f.write(f"{datetime.now()} | {line}\n")
                    f.flush()
                    if c >= 10:
                        c = 0
                        if self._check_cancel(task_id, task_step_id):
                            process.kill()
                            return False
            stderr_output = process.stderr.read()
            if stderr_output:
                f.write(f"{datetime.now()} | 错误输出:\n{stderr_output}\n")

            process.stdout.close()
            process.stderr.close()
            exit_code = process.wait()
            f.write(f"{datetime.now()} | 任务结束,退出代码:{exit_code}\n")
            if exit_code != 0:
                TrainTaskStep.objects.filter(id=task_step_id).update(
                    status=TrainTaskStatus.Failed, end_datetime=get_now()
                )
                return False
        TrainTaskStep.objects.filter(id=task_step_id).update(
            status=TrainTaskStatus.Succeed, end_datetime=get_now()
        )
        return True

    def _check_cancel(self, task_id, task_step_id) -> bool:
        """Checks if a training task has been canceled and updates the task log
        accordingly.

        Returns:
            bool: True if the task is canceled and the log is updated, False
            otherwise.
        """
        if TrainTask.objects.filter(id=task_id, status=TrainTaskStatus.Canceled).exists():
            TrainTaskStep.objects.filter(id=task_step_id).update(
                status=TrainTaskStatus.Canceled, end_datetime=get_now()
            )
            return True
        return False

    @property
    def name(self):
        return self._name
