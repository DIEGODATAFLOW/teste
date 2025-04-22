from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
from app.tasks import execute_scraping
from app.models import ScrapingRequest, TaskResponse, TaskStatus
import uuid

app = FastAPI()


@app.post("/start-scraping", response_model=TaskResponse)
async def start_scraping(request: ScrapingRequest):
    try:
        # Gera um ID único para a tarefa
        task_id = str(uuid.uuid4())

        # Adapta os dados para o seu scraping existente
        task_data = {
            "url": request.url,
            "parameters": request.parameters.dict()
            if hasattr(request.parameters, "dict")
            else request.parameters,
        }

        # Envia a tarefa para o Celery
        task = execute_scraping.apply_async(args=[task_data], task_id=task_id)

        return {
            "task_id": task_id,
            "status": TaskStatus.PENDING,
            "result": None,
            "error": None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/task-status/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    try:
        task_result = AsyncResult(task_id, app=execute_scraping)

        response_data = {
            "task_id": task_id,
            "status": TaskStatus(task_result.state),
            "result": None,
            "error": None,
        }

        if task_result.ready():
            if task_result.successful():
                response_data["result"] = task_result.result.get("result")
                response_data["status"] = TaskStatus.SUCCESS
            else:
                response_data["error"] = str(
                    task_result.result.get("error", "Unknown error")
                )
                response_data["status"] = TaskStatus.FAILURE

        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "Scraping System API"}
