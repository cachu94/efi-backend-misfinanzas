from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate

from src.database import get_session
from src.models.cuentas import (
    Cuenta,
    CuentaPublic,
    CuentaNested,
    CuentaCreate,
    CuentaUpdate,
)

router = APIRouter(
    prefix="/cuentas",
    tags=["Cuentas Financieras"]
)

error_404 = {
    404: {
        "description": "Cuenta no encontrada",
        "content": {
            "application/json": {"example": {"detail": "Cuenta no encontrada!"}}
        },
    }
}

@router.post("/", response_model=CuentaPublic, status_code=status.HTTP_201_CREATED)
def crear_cuenta(cuenta: CuentaCreate, db: Session = Depends(get_session)):
    db_cuenta = Cuenta.model_validate(cuenta)
    db.add(db_cuenta)
    db.commit()
    db.refresh(db_cuenta)
    return db_cuenta


@router.get("/", response_model=Page[CuentaPublic])
def listar_cuentas(db: Session = Depends(get_session)):
    query = select(Cuenta).where(Cuenta.activo == True)
    return paginate(db, query)

@router.get("/{cuenta_id}", response_model=CuentaNested, responses=error_404)
def obtener_cuenta(cuenta_id: int, db: Session = Depends(get_session)):
    cuenta = db.get(Cuenta, cuenta_id)
    if not cuenta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Cuenta no encontrada!"
        )
    return cuenta

@router.patch("/{cuenta_id}", response_model=CuentaPublic, responses=error_404)
def actualizar_cuenta(
    cuenta_id: int,
    cuenta_update: CuentaUpdate,
    db: Session = Depends(get_session),
):
    db_cuenta = db.get(Cuenta, cuenta_id)
    if not db_cuenta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Cuenta no encontrada!"
        )

    datos = cuenta_update.model_dump(exclude_unset=True)
    db_cuenta.sqlmodel_update(datos)

    db.add(db_cuenta)
    db.commit()
    db.refresh(db_cuenta)
    return db_cuenta


@router.delete("/{cuenta_id}", responses=error_404)
def eliminar_cuenta(cuenta_id: int, db: Session = Depends(get_session)):
    cuenta = db.get(Cuenta, cuenta_id)
    if not cuenta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Cuenta no encontrada!"
        )
    cuenta.activo = False

    db.add(cuenta)
    db.commit()
    db.refresh(cuenta)

    return {
        "mensaje": f"Cuenta {cuenta_id} desactivada correctamente",
        "activo": cuenta.activo,
    }