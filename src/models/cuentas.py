from typing import TYPE_CHECKING, Annotated

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .creditos import CreditoDeuda
    from .gastos_diarios import GastoDiario
    from .gastos_fijos import GastoFijo
    from .ingresos import Ingreso
    from .usuarios import Usuario, UsuarioPublic

NombreCuenta = Annotated[
    str, Field(min_length=2, max_length=50, description="Nombre de la cuenta")
]
TipoCuenta = Annotated[
    str,
    Field(min_length=3, max_length=50, description="Tipo: banco, billetera_virtual"),
]
EntidadFinanciera = Annotated[
    str | None,
    Field(default=None, max_length=100, description="Entidad financiera asociada"),
]


class CuentaBase(SQLModel):
    usuario_id: Annotated[
        int, Field(foreign_key="usuarios.id", description="ID del usuario asociado")
    ]
    nombre: NombreCuenta
    tipo_cuenta: TipoCuenta
    entidad: EntidadFinanciera = None
    activo: bool = True


class Cuenta(CuentaBase, table=True):
    __tablename__ = "cuentas"  # type: ignore

    id: Annotated[int | None, Field(default=None, primary_key=True)]

    usuario: "Usuario" = Relationship(back_populates="cuentas")
    ingresos: list["Ingreso"] = Relationship(back_populates="cuenta")
    gastos_fijos: list["GastoFijo"] = Relationship(back_populates="cuenta")
    creditos_deuda: list["CreditoDeuda"] = Relationship(back_populates="cuenta")
    gastos_diarios: list["GastoDiario"] = Relationship(back_populates="cuenta")


class CuentaPublic(CuentaBase):
    id: int


class CuentaNested(CuentaPublic):
    usuario: "UsuarioPublic"




#lo mismo que antes, te genero dos cuestiones que tengo que usar en los pads, fijate que te los voy a agregar en todos xd
class CuentaCreate(CuentaBase):
    pass


class CuentaUpdate(SQLModel):
    usuario_id: int | None = None
    nombre: str | None = Field(default=None, min_length=2, max_length=50)
    tipo_cuenta: str | None = Field(default=None, min_length=3, max_length=50)
    entidad: str | None = Field(default=None, max_length=100)
    activo: bool | None = None