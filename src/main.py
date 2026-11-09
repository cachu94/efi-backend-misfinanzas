from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from sqlmodel import SQLModel

import src.models
from src.database import engine
from src.routers import (
    creditos,
    cuentas,
    gastos_diarios,
    gastos_fijos,
    ingresos,
    metricas,
    usuarios,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title="Sistema de Finanzas Personales - API",
    lifespan=lifespan,
    description="""Backend modular desarrollado con FastAPI, SQLModel y SQLite.
    Permite el control integral del flujo financiero mensual, gestión de cuentas,
    baja lógica de gastos fijos, máquina de estados para créditos y cálculo
    dinámico de presupuesto diario hasta la fecha de cobro.""",
    version="1.0.0",
)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5500",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios.router)
app.include_router(cuentas.router)
app.include_router(ingresos.router)
app.include_router(gastos_fijos.router)
app.include_router(creditos.router)
app.include_router(gastos_diarios.router)
app.include_router(metricas.router)

add_pagination(app)


@app.get("/", tags=["Health Check"])
def inicio():
    return {"mesnaje": "Bienvenido a la API de Finanzas Personales"}
