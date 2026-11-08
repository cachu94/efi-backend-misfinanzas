from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Field, SQLModel, Session, select
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate

from src.database import get_session
from src.models.gastos_fijos import (
    GastoFijo,
    GastoFijoBase,
    GastoFijoPublic,
    GastoFijoNested,
    GastoFijoCreate,
    GastoFijoUpdate,
)


router = APIRouter(
    prefix="/gastos-fijos",
    tags=["Gastos Fijos"]
)

error_404 = {
    404: {
        "description": "Gasto fijo no encontrado",
        "content": {
            "application/json": {"example": {"detail": "Gasto fijo no encontrado!"}}
        },
    }
}


@router.post("/", response_model=GastoFijoPublic, status_code=status.HTTP_201_CREATED)
def crear_gasto_fijo(gasto: GastoFijoCreate, db: Session = Depends(get_session)):
    db_gasto = GastoFijo.model_validate(gasto)
    db.add(db_gasto)
    db.commit()
    db.refresh(db_gasto)
    return db_gasto


@router.get("/", response_model=Page[GastoFijoPublic])
def listar_gastos_fijos(db: Session = Depends(get_session)):
    query = select(GastoFijo).where(GastoFijo.activo == True)
    return paginate(db, query)


@router.get("/{gasto_id}", response_model=GastoFijoNested, responses=error_404)
def obtener_gasto_fijo(gasto_id: int, db: Session = Depends(get_session)):
    gasto = db.get(GastoFijo, gasto_id)
    if not gasto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Gasto fijo no encontrado!"
        )
    return gasto


@router.patch("/{gasto_id}", response_model=GastoFijoPublic, responses=error_404)
def actualizar_gasto_fijo(
    gasto_id: int,
    gasto_update: GastoFijoUpdate,
    db: Session = Depends(get_session),
):
    db_gasto = db.get(GastoFijo, gasto_id)
    if not db_gasto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Gasto fijo no encontrado!"
        )

    datos = gasto_update.model_dump(exclude_unset=True)
    db_gasto.sqlmodel_update(datos)

    db.add(db_gasto)
    db.commit()
    db.refresh(db_gasto)
    return db_gasto


@router.delete("/{gasto_id}", responses=error_404)
def eliminar_gasto_fijo(gasto_id: int, db: Session = Depends(get_session)):
    gasto = db.get(GastoFijo, gasto_id)
    if not gasto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Gasto fijo no encontrado!"
        )
    
    gasto.activo = False
    gasto.fecha_baja = date.today()

    db.add(gasto)
    db.commit()
    db.refresh(gasto)

    return {
        "mensaje": f"Gasto fijo {gasto_id} cancelado correctamente",
        "activo": gasto.activo,
        "fecha_baja": gasto.fecha_baja,
    }