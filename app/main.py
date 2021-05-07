from fastapi import FastAPI, Request
from sqlalchemy import create_engine
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils import get_parameter_from_ssm
from routes import api_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException
from starlette.responses import UJSONResponse
from fastapi.encoders import jsonable_encoder
app = FastAPI()
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def http_exception_handler(request: Request, exc: HTTPException) -> UJSONResponse:
    return UJSONResponse(status_code=exc.status_code, content=jsonable_encoder(exc.detail))
# include routes
app.include_router(api_router)
app.add_exception_handler(HTTPException, http_exception_handler)
