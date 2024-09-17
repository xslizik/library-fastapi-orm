from fastapi import FastAPI
from dbs_assignment.router import router
from dbs_assignment.database import Base, engine
from dbs_assignment.models import *

from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError

Base.metadata.create_all(engine)

app = FastAPI(title="DBS")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return Response("Invalid data", status_code=status.HTTP_400_BAD_REQUEST)

app.include_router(router)
