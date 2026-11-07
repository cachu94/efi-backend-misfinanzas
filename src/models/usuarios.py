from typing import TYPE_CHECKING, Annotated

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .creditos import CreditoDeuda, CreditoDeudaPublic
    from .cuentas import Cuenta, CuentaPublic
    from .gastos_diarios import GastoDiario, GastoDiarioPublic
    from .gastos_fijos import GastoFijo, GastoFijoPublic
    from .ingresos import Ingreso, IngresoPublic

NombreUser = Annotated[
    str, Field(min_length=3, max_length=50, description="Nombre de usuario")
]
EmailUser = Annotated[str, Field(max_length=255, description="Correo electrónico")]
DiaCobro = Annotated[int, Field(ge=1, le=31, description="Día de cobro")]
PorcentajeAhorro = Annotated[
    float, Field(default=0.0, ge=0.0, le=100.0, description="Porcentaje")
]


class UsuarioBase(SQLModel):
    nombre: NombreUser
    email: EmailUser
    dia_cobro: DiaCobro
    porcentaje_ahorro: PorcentajeAhorro = 0.0


class Usuario(UsuarioBase, table=True):
    __tablename__ = "usuarios"  # type: ignore

    id: Annotated[int | None, Field(default=None, primary_key=True)]

    ingresos: list["Ingreso"] = Relationship(back_populates="usuario")
    cuentas: list["Cuenta"] = Relationship(back_populates="usuario")
    gastos_fijos: list["GastoFijo"] = Relationship(back_populates="usuario")
    creditos_deuda: list["CreditoDeuda"] = Relationship(back_populates="usuario")
    gastos_diarios: list["GastoDiario"] = Relationship(back_populates="usuario")


class UsuarioPublic(UsuarioBase):
    id: int


class UsuarioNested(UsuarioPublic):
    ingresos: list["IngresoPublic"] = []
    cuentas: list["CuentaPublic"] = []
    gastos_fijos: list["GastoFijoPublic"] = []
    creditos_deuda: list["CreditoDeudaPublic"] = []
    gastos_diarios: list["GastoDiarioPublic"] = []
