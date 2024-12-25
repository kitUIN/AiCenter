import threading

from fastapi import Request, HTTPException

from pydantic import BaseModel
from .heart import send_heartbeat, app
from .pulc import PULCPlugin
from sdk.plugin_tool import PlanTemplate, ApiDocData, ArgData, PowerData

threading.Thread(target=send_heartbeat, daemon=True).start()


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


@app.post("/upload")
async def upload(request: Request):
    content_type = request.headers.get('Content-Type')

    if content_type == "application/json":
        data = await request.json()
        return {"message": "Received JSON", "data": data}

    elif content_type == "multipart/form-data":
        form_data = await request.form()
        return {"message": "Received multipart form data", "data": dict(form_data)}

    else:
        raise HTTPException(status_code=400, detail="Unsupported content type")
