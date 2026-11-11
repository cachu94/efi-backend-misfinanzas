from datetime import date
from typing import TYPE_CHECKING, Annotated, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .cuentas import Cuenta, CuentaPublic
    from .usuarios import Usuario, UsuarioPublic

EntidadAcreedora = Annotated[
    str,
    Field(
        min_length=2, max_length=100, description="Entidad o acreedor (ej. ICBC, MP)"
    ),
]
Descripcion = Annotated[
    str, Field(min_length=3, max_length=150, description="Detalle del crédito")
]
MontoCuota = Annotated[float, Field(gt=0, description="Monto de la cuota mensual")]
CantCuotas = Annotated[int, Field(ge=1, description="Números de cuotas")]


class CreditoDeudaBase(SQLModel):
    usuario_id: Annotated[
        int, Field(foreign_key="usuarios.id", description="ID del usuario asociado")
    ]
    cuenta_id: Annotated[
        int | None,
        Field(
            default=None,
            foreign_key="cuentas.id",
            description="ID de la cuenta asociada",
        ),
    ] = None
    entidad_acreedora: EntidadAcreedora
    descripcion: Descripcion
    precio_contado: Annotated[float | None, Field(default=None, gt=0)] = None
    monto_cuota: MontoCuota
    total_cuotas: CantCuotas
    cuota_actual: Annotated[
        int, Field(default=0, ge=0, description="Cuota actual / pagada del crédito")
    ] = 0
    fecha_inicio: date
    estado: Annotated[
        str, Field(default="activo", description="activo | finalizada | cancelada")
    ] = "activo"


class CreditoDeuda(CreditoDeudaBase, table=True):
    __tablename__ = "creditos_deuda"  # type: ignore

    id: Annotated[int | None, Field(default=None, primary_key=True)] = None

    usuario: "Usuario" = Relationship(back_populates="creditos_deuda")
    cuenta: Optional["Cuenta"] = Relationship(back_populates="creditos_deuda")


class CreditoDeudaPublic(CreditoDeudaBase):
    id: int


class CreditoDeudaNested(CreditoDeudaPublic):
    usuario: "UsuarioPublic"
    cuenta: "CuentaPublic | None" = None


# Facu te agrego estas dependencias porque las necesito para los path operations (los podia hacer en el route, pero lo pongo aca para que sea mas semantico)...


class CreditoDeudaCreate(CreditoDeudaBase):
    pass


class CreditoDeudaUpdate(SQLModel):
    usuario_id: int | None = None
    cuenta_id: int | None = None
    entidad_acreedora: str | None = Field(default=None, min_length=2, max_length=100)
    descripcion: str | None = Field(default=None, min_length=3, max_length=150)
    precio_contado: float | None = Field(default=None, gt=0)
    monto_cuota: float | None = Field(default=None, gt=0)
    total_cuotas: int | None = Field(default=None, ge=1)
    cuota_actual: int | None = Field(default=None, ge=0)
    fecha_inicio: str | None = None
    estado: str | None = Field(
        default=None, description="activo | finalizada | cancelada"
    )
