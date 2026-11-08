from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate

from src.database import get_session
from src.models.creditos import (
    CreditoDeuda,
    CreditoDeudaPublic,
    CreditoDeudaNested,
    CreditoDeudaCreate,
    CreditoDeudaUpdate,
)


router = APIRouter(
    prefix="/creditos",
    tags=["Créditos y Deudas"]
)

error_404 = {
    404: {
        "description": "Crédito no encontrado",
        "content": {
            "application/json": {"example": {"detail": "Crédito no encontrado!"}}
        },
    }
}

@router.post("/", response_model=CreditoDeudaPublic, status_code=status.HTTP_201_CREATED)
def crear_credito(credito: CreditoDeudaCreate, db: Session = Depends(get_session)):
    db_credito = CreditoDeuda.model_validate(credito)

    db.add(db_credito)
    db.commit()
    db.refresh(db_credito)
    return db_credito

@router.get("/", response_model=Page[CreditoDeudaPublic])
def listar_creditos(db: Session = Depends(get_session)):
    query = select(CreditoDeuda).where(CreditoDeuda.estado != "cancelada")
    return paginate(db, query)

@router.get("/{credito_id}", response_model=CreditoDeudaNested, responses=error_404)
def obtener_credito(credito_id: int, db: Session = Depends(get_session)):
    credito = db.get(CreditoDeuda, credito_id)
    if not credito:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crédito no encontrado!")
    return credito

@router.patch("/{credito_id}", response_model=CreditoDeudaPublic, responses=error_404)
def actualizar_credito(
    credito_id: int,
    credito_update: CreditoDeudaUpdate,
    db: Session = Depends(get_session),
):
    db_credito = db.get(CreditoDeuda, credito_id)
    if not db_credito:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crédito no encontrado!")

    datos = credito_update.model_dump(exclude_unset=True)
    db_credito.sqlmodel_update(datos)

    if db_credito.cuota_actual >= db_credito.total_cuotas:
        db_credito.estado = "finalizada"

    db.add(db_credito)
    db.commit()
    db.refresh(db_credito)
    return db_credito

@router.delete("/{credito_id}", responses=error_404)
def eliminar_credito(credito_id: int, db: Session = Depends(get_session)):
    credito = db.get(CreditoDeuda, credito_id)
    if not credito:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crédito no encontrado!")

    credito.estado = "cancelada"

    db.add(credito)
    db.commit()
    db.refresh(credito)

    return {"mensaje": f"Crédito {credito_id} fue cancelado correctamente", "estado": credito.estado}

# Endpoint de negocio
@router.post("/{credito_id}/registrar-pago", response_model=CreditoDeudaPublic, responses=error_404)
def registrar_pago_cuota(credito_id: int, db: Session = Depends(get_session)):
    credito = db.get(CreditoDeuda, credito_id)
    if not credito:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crédito no encontrado!")

    if credito.estado == "finalizada" or credito.cuota_actual >= credito.total_cuotas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El crédito ya se encuentra anulado o finalizado!"
        )

    credito.cuota_actual += 1

    if credito.cuota_actual == credito.total_cuotas:
        credito.estado = "finalizada"

    db.add(credito)
    db.commit()
    db.refresh(credito)
    return credito