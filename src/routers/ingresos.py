from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Field, SQLModel, Session, select
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate

from src.database import get_session
from src.models.ingresos import (
    Ingreso,
    IngresoBase,
    IngresoPublic,
    IngresoNested,
    IngresoCreate,
    IngresoUpdate,
)

router = APIRouter(
    prefix="/ingresos",
    tags=["Ingresos"]
)

error_404 = {
    404: {
        "description": "Ingreso no encontrado",
        "content": {
            "application/json": {"example": {"detail": "Ingreso no encontrado!"}}
        },
    }
}


@router.post("/", response_model=IngresoPublic, status_code=status.HTTP_201_CREATED)
def crear_ingreso(ingreso: IngresoCreate, db: Session = Depends(get_session)):
    db_ingreso = Ingreso.model_validate(ingreso)
    db.add(db_ingreso)
    db.commit()
    db.refresh(db_ingreso)
    return db_ingreso


@router.get("/", response_model=Page[IngresoPublic])
def listar_ingresos(db: Session = Depends(get_session)):
    query = select(Ingreso).order_by(Ingreso.fecha_ingreso.desc())
    return paginate(db, query)


@router.get("/{ingreso_id}", response_model=IngresoNested, responses=error_404)
def obtener_ingreso(ingreso_id: int, db: Session = Depends(get_session)):
    ingreso = db.get(Ingreso, ingreso_id)
    if not ingreso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Ingreso no encontrado!"
        )
    return ingreso


@router.patch("/{ingreso_id}", response_model=IngresoPublic, responses=error_404)
def actualizar_ingreso(
    ingreso_id: int,
    ingreso_update: IngresoUpdate,
    db: Session = Depends(get_session),
):
    db_ingreso = db.get(Ingreso, ingreso_id)
    if not db_ingreso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Ingreso no encontrado!"
        )

    datos = ingreso_update.model_dump(exclude_unset=True)
    db_ingreso.sqlmodel_update(datos)

    db.add(db_ingreso)
    db.commit()
    db.refresh(db_ingreso)
    return db_ingreso


@router.delete("/{ingreso_id}", status_code=status.HTTP_204_NO_CONTENT, responses=error_404)
def eliminar_ingreso(ingreso_id: int, db: Session = Depends(get_session)):
    ingreso = db.get(Ingreso, ingreso_id)
    if not ingreso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Ingreso no encontrado!"
        )

    db.delete(ingreso)
    db.commit()