import os
import sys
from pathlib import Path

from center.tasks.workflow.steps.base import BaseWorkflowStep


class VenvWorkflowStep(BaseWorkflowStep):
    def _run(self, env_name: Path, cmd: str, task_id: int, task_step_id: int, **kwargs) -> bool:
        venv_path = env_name.joinpath("venv")
        return super()._run(env_name, f"{sys.executable} -m venv {venv_path}", task_id, task_step_id, **kwargs)


class NormalVenvWorkflowStep(BaseWorkflowStep):
    def _run(self, env_name: Path, cmd: str, task_id: int, task_step_id: int, **kwargs) -> bool:
        venv_activate = env_name.joinpath(
            "venv",
            "bin",
            "activate"
        ) if os.name != "nt" else env_name.joinpath("venv",
                                                    "Scripts",
                                                    "activate.bat")
        return super()._run(env_name, f"{venv_activate} && {cmd}", task_id, task_step_id, **kwargs)
