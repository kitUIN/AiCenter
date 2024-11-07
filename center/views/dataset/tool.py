from datetime import datetime, timezone

from label_studio_sdk import ProjectsCreateResponse
from label_studio_sdk.client import LabelStudio

from application.settings import LABEL_STUDIO_URL, LABEL_STUDIO_APIKEY


def label_studio_create_project(name: str, description: str | None = None):
    """创建项目

    @param name: 项目名称
    @param description: 项目描述
    @return: 项目ID,项目创建时间
    @raise: label_studio_sdk.core.api_error.ApiError
    """
    ls = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_APIKEY)
    project = ls.projects.create(
        title=name,
        description=description,
    )  # type: ProjectsCreateResponse
    res = project.dict()
    # date_string = res["created_at"]
    # create_date_time = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    # create_date_time = create_date_time.replace(tzinfo=timezone.utc)
    return res["id"]
