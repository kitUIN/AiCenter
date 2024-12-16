from pathlib import Path

import requests

import jenkins

from application.settings import JENKINS_URL, JENKINS_USERNAME, JENKINS_PASSWORD
from center.models import TrainTask

_jenkins_server = jenkins.Jenkins(JENKINS_URL, JENKINS_USERNAME, JENKINS_PASSWORD)


def get_jenkins_server():
    return _jenkins_server


class JenkinsManager:
    def __init__(self):
        self.server = get_jenkins_server()

    def create_job(self, name, pipeline_script, description: str = "", sandbox: bool = True):
        pipeline_config_xml = f"""<?xml version='1.1' encoding='UTF-8'?>
        <flow-definition plugin="workflow-job@2.40">
          <description>{description}</description>
          <keepDependencies>false</keepDependencies>
          <properties/>
          <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps@2.92">
            <script>{pipeline_script}</script>
            <sandbox>{"true" if sandbox else "false"}</sandbox>
          </definition>
          <triggers/>
        </flow-definition>
        """
        try:
            res = self.server.create_job(name, pipeline_config_xml)
            return True, res
        except Exception as e:
            return False, str(e)

    def stop_build(self, task: TrainTask):
        return self.server.stop_build(task.plan.name, task.number)

    def download_task_artifacts(self, task: TrainTask):
        res = self.server.get_build_info(task.plan.name, task.number)
        for i in res["artifacts"]:
            r = requests.get(f'{JENKINS_URL}/job/{task.plan.name}/{task.number}/artifact/{i["relativePath"]}',
                             stream=True)
            filename = Path(f'artifact/{task.plan.name}/{task.number}/{i["relativePath"]}')
            folder = filename.parent
            if not folder.exists():
                folder.mkdir(parents=True, exist_ok=True)
            with open(filename, "wb") as f:
                for bl in r.iter_content(chunk_size=1024):
                    if bl:
                        f.write(bl)


_jenkins_manager = JenkinsManager()


def get_jenkins_manager() -> JenkinsManager:
    return _jenkins_manager


__all__ = [
    "get_jenkins_manager",
    "get_jenkins_server",
    "JenkinsManager",
]
