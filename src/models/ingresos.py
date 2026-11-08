from datetime import date
from typing import TYPE_CHECKING, Annotated, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .cuentas import Cuenta, CuentaPublic
    from .usuarios import Usuario, UsuarioPublic

Descripcion = Annotated[
    str, Field(min_length=3, max_length=150, description="Descripción del ingreso")
]
Monto = Annotated[float, Field(gt=0, description="Monto del ingreso (Mayor a 0)")]


class IngresoBase(SQLModel):
    usuario_id: Annotated[
        int, Field(foreign_key="usuarios.id", description="ID del usuario asociado")
    ]
    cuenta_id: Annotated[
        int | None,
        Field(
            default=None,
            foreign_key="cuentas.id",
            description="Cuenta donde ingresa el dinero",
        ),
    ] = None
    descripcion: Descripcion
    monto: Monto
    fecha_ingreso: date
    es_recurrente: bool = True


class Ingreso(IngresoBase, table=True):
    __tablename__ = "ingresos"  # type: ignore

    id: Annotated[int | None, Field(default=None, primary_key=True)]

    usuario: "Usuario" = Relationship(back_populates="ingresos")
    cuenta: Optional["Cuenta"] = Relationship(back_populates="ingresos")


class IngresoPublic(IngresoBase):
    id: int


class IngresoNested(IngresoPublic):
    usuario: "UsuarioPublic"
    cuenta: "CuentaPublic | None" = None

# --------------------------------------------------------
class IngresoCreate(IngresoBase):
    pass


class IngresoUpdate(SQLModel):
    usuario_id: int | None = None
    cuenta_id: int | None = None
    descripcion: str | None = Field(default=None, min_length=2, max_length=150)
    monto: float | None = Field(default=None, gt=0)
    fecha_ingreso: date | None = None
    es_recurrente: bool | None = None