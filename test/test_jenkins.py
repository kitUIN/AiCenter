import jenkins

server = jenkins.Jenkins('http://localhost:9095', "kulujun", "balabala")


def get_artifacts():
    last_build_number = server.get_job_info("11")['lastCompletedBuild']['number']
    build_info = server.get_build_info("11", last_build_number)
    artifacts = build_info.get('artifacts', [])


pipeline_name = "jenkins测试"

# 定义 Pipeline 脚本（Jenkinsfile）
pipeline_script = """
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }
        stage('Test') {
            steps {
                echo 'Testing...'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying...'
            }
        }
    }
}
"""
pipeline_config_xml = f"""<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job@2.40">
  <description>Example Pipeline</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps@2.92">
    <script>{pipeline_script}</script>
    <sandbox>true</sandbox>
  </definition>
  <triggers/>
</flow-definition>
"""
# res = server.build_job(pipeline_name)
# print(res)
# next_build_number = server.get_job_info(pipeline_name)['nextBuildNumber']
# build_info = server.build_job(pipeline_name)
# print(build_info)
# print(server.get_queue_info())
# print(server.get_running_builds())
# res = server.get_build_info("33", 2)
# print(res)

import requests
from pathlib import Path

res = server.get_build_info("33", 2)
for i in res["artifacts"]:
    r = requests.get(f'http://localhost:9095/job/33/2/artifact/{i["relativePath"]}', stream=True)
    filename = Path(f'power/33/2/{i["relativePath"]}')
    folder = filename.parent
    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)
    with open(filename, "wb") as f:
        for bl in r.iter_content(chunk_size=1024):
            if bl:
                f.write(bl)
