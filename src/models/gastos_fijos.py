from datetime import date
from typing import TYPE_CHECKING, Annotated, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .cuentas import Cuenta, CuentaPublic
    from .usuarios import Usuario, UsuarioPublic

Categoria = Annotated[
    str,
    Field(
        min_length=3, max_length=50, description="Categoría (ej. Servicios, Alquiler)"
    ),
]
Descripcion = Annotated[
    str, Field(min_length=3, max_length=150, description="Descripción del servicio")
]
Monto = Annotated[float, Field(gt=0, description="Monto del gasto fijo (Mayor a 0)")]
DiaVencimiento = Annotated[
    int, Field(ge=1, le=31, description="Día del mes en que vence")
]


class GastoFijoBase(SQLModel):
    usuario_id: Annotated[
        int, Field(foreign_key="usuarios.id", description="ID del usuario asociado")
    ]
    cuenta_id: Annotated[
        int | None,
        Field(
            default=None,
            foreign_key="cuentas.id",
            description="Cuenta en que se debita",
        ),
    ] = None
    categoria: Categoria
    descripcion: Descripcion
    monto: Monto
    dia_vencimiento: DiaVencimiento
    activo: bool = True
    fecha_baja: date | None = None


class GastoFijo(GastoFijoBase, table=True):
    __tablename__ = "gastos_fijos"  # type: ignore

    id: Annotated[int | None, Field(default=None, primary_key=True)] = None

    usuario: "Usuario" = Relationship(back_populates="gastos_fijos")
    cuenta: Optional["Cuenta"] = Relationship(back_populates="gastos_fijos")


class GastoFijoPublic(GastoFijoBase):
    id: int


class GastoFijoNested(GastoFijoPublic):
    usuario: "UsuarioPublic"
    cuenta: "CuentaPublic | None" = None


# ----------------------------------------------------
class GastoFijoCreate(GastoFijoBase):
    pass


class GastoFijoUpdate(SQLModel):
    usuario_id: int | None = None
    cuenta_id: int | None = None
    categoria: str | None = Field(default=None, min_length=2, max_length=50)
    descripcion: str | None = Field(default=None, min_length=3, max_length=150)
    monto: float | None = Field(default=None, gt=0)
    dia_vencimiento: int | None = Field(default=None, ge=1, le=31)
    activo: bool | None = None
    fecha_baja: date | None = None
