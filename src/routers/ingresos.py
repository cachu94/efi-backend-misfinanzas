from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import Session, select

from src.database import get_session
from src.models.ingresos import (
    Ingreso,
    IngresoCreate,
    IngresoNested,
    IngresoPublic,
    IngresoUpdate,
)

router = APIRouter(prefix="/ingresos", tags=["Ingresos"])

error_404 = {
    404: {
        "description": "Ingreso no encontrado",
        "content": {
            "application/json": {"example": {"detail": "Ingreso no encontrado!"}}
        },
    }
}


@router.post("/", response_model=IngresoPublic, status_code=status.HTTP_201_CREATED)
def crear_ingreso(ingreso: IngresoCreate, db: Session = Depends(get_session)):  # noqa: B008
    db_ingreso = Ingreso.model_validate(ingreso)
    db.add(db_ingreso)
    db.commit()
    db.refresh(db_ingreso)
    return db_ingreso


@router.get("/", response_model=Page[IngresoPublic])
def listar_ingresos(db: Session = Depends(get_session)):  # noqa: B008
    query = select(Ingreso).order_by(Ingreso.fecha_ingreso.desc())  # type: ignore
    return paginate(db, query)  # type: ignore


@router.get("/{ingreso_id}", response_model=IngresoNested, responses=error_404)  # type: ignore
def obtener_ingreso(ingreso_id: int, db: Session = Depends(get_session)):  # noqa: B008
    ingreso = db.get(Ingreso, ingreso_id)
    if not ingreso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ingreso no encontrado!"
        )
    return ingreso


@router.patch("/{ingreso_id}", response_model=IngresoPublic, responses=error_404)  # type: ignore
def actualizar_ingreso(
    ingreso_id: int,
    ingreso_update: IngresoUpdate,
    db: Session = Depends(get_session),  # noqa: B008
):
    db_ingreso = db.get(Ingreso, ingreso_id)
    if not db_ingreso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ingreso no encontrado!"
        )

    datos = ingreso_update.model_dump(exclude_unset=True)
    db_ingreso.sqlmodel_update(datos)

    db.add(db_ingreso)
    db.commit()
    db.refresh(db_ingreso)
    return db_ingreso


@router.delete(
    "/{ingreso_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=error_404,  # type: ignore
)
def eliminar_ingreso(ingreso_id: int, db: Session = Depends(get_session)):  # noqa: B008
    ingreso = db.get(Ingreso, ingreso_id)
    if not ingreso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ingreso no encontrado!"
        )

    db.delete(ingreso)
    db.commit()
