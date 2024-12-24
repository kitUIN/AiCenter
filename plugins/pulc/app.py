import threading

from fastapi import FastAPI, Request, HTTPException

from .heart import send_heartbeat
from .pulc import PULCPlugin
from sdk.plugin_tool import PlanTemplate, ApiDocData, ArgData

app = FastAPI()

threading.Thread(target=send_heartbeat, daemon=True).start()

@app.get("/health")
async def health():
    return "ok"


@app.get("/plugin/plan/template", response_model=PlanTemplate)
async def plan_template():
    plugin = PULCPlugin()
    return plugin.get_plan_template()


@app.get("/plugin/api/doc", response_model=ApiDocData)
async def plan_template():
    plugin = PULCPlugin()
    return plugin.get_api_doc()


@app.get("/plugin/power/args", response_model=list[ArgData])
async def plan_template(request: Request):
    plugin = PULCPlugin()
    return plugin.get_power_args()


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
