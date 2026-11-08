from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Field, SQLModel, Session, select
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate

from src.database import get_session
from src.models.usuarios import (
    Usuario,
    UsuarioBase,
    UsuarioPublic,
    UsuarioNested,
    UsuarioCreate,
    UsuarioUpdate,
)


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

error_404 = {
    404: {
        "description": "Usuario no encontrado",
        "content": {
            "application/json": {"example": {"detail": "Usuario no encontrado!"}}
        },
    }
}


@router.post("/", response_model=UsuarioPublic, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_session)):
    db_usuario = Usuario.model_validate(usuario)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@router.get("/", response_model=Page[UsuarioPublic])
def listar_usuarios(db: Session = Depends(get_session)):
    query = select(Usuario)
    return paginate(db, query)


@router.get("/{usuario_id}", response_model=UsuarioNested, responses=error_404)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_session)):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuario no encontrado!"
        )
    return usuario


@router.patch("/{usuario_id}", response_model=UsuarioPublic, responses=error_404)
def actualizar_usuario(
    usuario_id: int,
    usuario_update: UsuarioUpdate,
    db: Session = Depends(get_session),
):
    db_usuario = db.get(Usuario, usuario_id)
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuario no encontrado!"
        )

    datos = usuario_update.model_dump(exclude_unset=True)
    db_usuario.sqlmodel_update(datos)

    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT, responses=error_404)
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_session)):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuario no encontrado!"
        )

    db.delete(usuario)
    db.commit()