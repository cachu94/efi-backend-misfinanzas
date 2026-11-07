from datetime import date
from typing import TYPE_CHECKING, Annotated, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .cuentas import Cuenta, CuentaPublic
    from .usuarios import Usuario, UsuarioPublic

CategoriaGasto = Annotated[
    str,
    Field(
        min_length=2, max_length=50, description="Categoría (Ej. Supermercado, Ocio)"
    ),
]
MontoGasto = Annotated[float, Field(gt=0, description="Monto gastado")]
Nota = Annotated[
    str | None, Field(default=None, max_length=255, description="Nota adicional")
]


class GastoDiarioBase(SQLModel):
    usuario_id: Annotated[
        int, Field(foreign_key="usuarios.id", description="ID del usuario asociado")
    ]
    cuenta_id: Annotated[
        int | None,
        Field(
            default=None,
            foreign_key="cuentas.id",
            description="Cuenta o billetera utilizada",
        ),
    ] = None
    categoria: CategoriaGasto
    monto: MontoGasto
    fecha: date
    notas: Nota = None


class GastoDiario(GastoDiarioBase, table=True):
    __tablename__ = "gastos_diarios"  # type: ignore

    id: Annotated[int | None, Field(default=None, primary_key=True)]

    usuario: "Usuario" = Relationship(back_populates="gastos_diarios")
    cuenta: Optional["Cuenta"] = Relationship(back_populates="gastos_diarios")


class GastoDiarioPublic(GastoDiarioBase):
    id: int


class GastoDiarioNested(GastoDiarioPublic):
    usuario: "UsuarioPublic"
    cuenta: "CuentaPublic | None" = None
