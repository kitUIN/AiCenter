import logging

from pathlib import Path
from typing import Literal

from celery.app import shared_task

from center.models.workflow import TrainTask, TrainTaskStep
from center.tasks.workflow import VenvWorkflowStep, NormalVenvWorkflowStep, get_now
from enums import TrainTaskStatus
from plugin import get_plugin_templates
from plugin.plugin_tool import TaskStepData

logger = logging.getLogger(__name__)


class TrainTaskManager:
    def __init__(self, env_name: str, task_id: int):
        self.task_id = task_id
        self.env_name = Path(env_name)

    def run_step(self, task_step_id, name: str, step_type: Literal["normal", "venv"], cmd: str, **kwargs):
        if step_type == "venv":
            step = VenvWorkflowStep(name=name)
        else:
            step = NormalVenvWorkflowStep(name=name)
        return step.run(self.env_name, cmd, self.task_id, task_step_id, **kwargs)

    def run_steps(self, steps: list[TaskStepData]):
        for step in self.init_steps(steps=steps):
            if not self.run_step(**step):
                return False
        TrainTask.objects.filter(id=self.task_id).update(status=TrainTaskStatus.Succeed, finished_datetime=get_now())
        return True

    def init_steps(self, steps: list[TaskStepData]):
        res = []
        for step in steps:
            t = step.__dict__
            step_model = TrainTaskStep.objects.create(task_id=self.task_id, name=step.name)
            t["task_step_id"] = step_model.id
            res.append(t)
        return res


@shared_task(ignore_result=True, routing_key='train', exchange='train')
def start_train(task_id: int):
    task = TrainTask.objects.get(id=task_id)
    task.status = TrainTaskStatus.Running
    task.save()
    key = task.ai_model.key
    templates = get_plugin_templates()
    if key not in templates.keys():
        return "无对应的插件配置文件"
    venv_name = f"train_task/{task.plan.name}_{task.id}"
    manager = TrainTaskManager(venv_name, task.id)
    return manager.run_steps(templates[key]().get_task_steps(
        requirements=task.plan.requirements.file.path if task.plan.requirements else None,
        startup_cmd=task.plan.get_startup_cmd(f"result/{task.id}")
    ))
