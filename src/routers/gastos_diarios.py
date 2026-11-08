from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Field, SQLModel, Session, select
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from datetime import date

from src.database import get_session
from src.models.gastos_diarios import (
    GastoDiario,
    GastoDiarioBase,
    GastoDiarioPublic,
    GastoDiarioNested,
    GastoDiarioCreate,
    GastoDiarioUpdate,
)

router = APIRouter(
    prefix="/gastos-diarios",
    tags=["Gastos Diarios"]
)

error_404 = {
    404: {
        "description": "Gasto diario no encontrado",
        "content": {
            "application/json": {"example": {"detail": "Gasto diario no encontrado!"}}
        },
    }
}

@router.post("/", response_model=GastoDiarioPublic, status_code=status.HTTP_201_CREATED)
def crear_gasto_diario(gasto: GastoDiarioCreate, db: Session = Depends(get_session)):
    db_gasto = GastoDiario.model_validate(gasto)
    db.add(db_gasto)
    db.commit()
    db.refresh(db_gasto)
    return db_gasto


@router.get("/", response_model=Page[GastoDiarioPublic])
def listar_gastos_diarios(db: Session = Depends(get_session)):
    query = select(GastoDiario).order_by(GastoDiario.fecha.desc())
    return paginate(db, query)


@router.get("/{gasto_id}", response_model=GastoDiarioNested, responses=error_404)
def obtener_gasto_diario(gasto_id: int, db: Session = Depends(get_session)):
    gasto = db.get(GastoDiario, gasto_id)
    if not gasto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Gasto diario no encontrado!"
        )
    return gasto


@router.patch("/{gasto_id}", response_model=GastoDiarioPublic, responses=error_404)
def actualizar_gasto_diario(
    gasto_id: int,
    gasto_update: GastoDiarioUpdate,
    db: Session = Depends(get_session),
):
    db_gasto = db.get(GastoDiario, gasto_id)
    if not db_gasto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Gasto diario no encontrado!"
        )

    datos = gasto_update.model_dump(exclude_unset=True)
    db_gasto.sqlmodel_update(datos)

    db.add(db_gasto)
    db.commit()
    db.refresh(db_gasto)
    return db_gasto


@router.delete("/{gasto_id}", status_code=status.HTTP_204_NO_CONTENT, responses=error_404)
def eliminar_gasto_diario(gasto_id: int, db: Session = Depends(get_session)):
    gasto = db.get(GastoDiario, gasto_id)
    if not gasto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Gasto diario no encontrado!"
        )

    db.delete(gasto)
    db.commit()