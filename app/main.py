from fastapi import FastAPI, Request
from app.routers.db import router as db_router
from app.routers.log_management import fastapi_logger
import time

app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Метла, добавляющая заголовок, показывающий время, за которое обработалась ручка
    """
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    fastapi_logger.info(f'It took {str(process_time)} seconds to respond')
    return response


@app.middleware("http")
async def log_tracking_func(request: Request, call_next):
    """
    Метла, логирующая информацию о методах, ЮРЛах и клиентов
    """
    client_ip = request.client.host
    client_port = request.client.port
    method = request.method
    url = request.url.path
    fastapi_logger.info(f'Request: {method} {url} from {client_ip}:{client_port}')
    response = await call_next(request)
    status_code = response.status_code
    fastapi_logger.info(f'Response: {method} {url} returned {status_code} to {client_ip}:{client_port}')
    return response


app.include_router(db_router)