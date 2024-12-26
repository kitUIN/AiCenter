import threading

from fastapi import Request, HTTPException, Form, File, UploadFile

from pydantic import BaseModel
from .heart import start_heartbeat, app
from .pulc import PULCPlugin
from sdk.plugin_tool import PlanTemplate, ApiDocData, ArgData, PowerData, PredictFile

threading.Thread(target=start_heartbeat, daemon=True).start()


class BaseResponse(BaseModel):
    code: int
    msg: str


class PlanTemplateResponse(BaseResponse):
    data: PlanTemplate


class ApiDocDataResponse(BaseResponse):
    data: ApiDocData


class ArgDataResponse(BaseResponse):
    data: list[ArgData]


@app.get("/health")
async def health():
    return "ok"


@app.get("/plugin/plan/template", response_model=PlanTemplateResponse)
async def plan_template():
    plugin = PULCPlugin()
    data = plugin.get_plan_template()
    return {"code": 200, "msg": "success", "data": data}


@app.get("/plugin/api/doc", response_model=ApiDocDataResponse)
async def plan_template():
    plugin = PULCPlugin()
    data = plugin.get_api_doc()
    return {"code": 200, "msg": "success", "data": data}


@app.post("/plugin/power/args", response_model=ArgDataResponse)
async def plan_template(request: Request, item: PowerData):
    plugin = PULCPlugin()
    data = plugin.get_power_args(**item.model_dump())
    return {"code": 200, "msg": "success", "data": data}


@app.post("/plugin/build/success")
async def build_success(request: Request):
    plugin = PULCPlugin()
    plugin.callback_task_success(request.json())
    return {"code": 200, "msg": "success"}


@app.post("/plugin/predict")
async def upload(request: Request, ):
    form_data = await request.form()
    print(form_data)
    plugin = PULCPlugin()
    files = []
    kwargs = {}
    for key, value in form_data.items():
        print(key, value)
        if key == "files":
            files.append(PredictFile(name=value.filename, content=value.file.read()))
        else:
            kwargs[key] = value
    res = plugin.predict(request, "", files, kwargs)
    return res
