from .creditos import (
    CreditoDeuda,
    CreditoDeudaBase,
    CreditoDeudaNested,
    CreditoDeudaPublic,
)
from .cuentas import Cuenta, CuentaBase, CuentaNested, CuentaPublic
from .gastos_diarios import (
    GastoDiario,
    GastoDiarioBase,
    GastoDiarioNested,
    GastoDiarioPublic,
)
from .gastos_fijos import GastoFijo, GastoFijoBase, GastoFijoNested, GastoFijoPublic
from .ingresos import Ingreso, IngresoBase, IngresoNested, IngresoPublic
from .usuarios import Usuario, UsuarioBase, UsuarioNested, UsuarioPublic

_types_namespace = {
    "UsuarioPublic": UsuarioPublic,
    "CuentaPublic": CuentaPublic,
    "IngresoPublic": IngresoPublic,
    "GastoFijoPublic": GastoFijoPublic,
    "GastoDiarioPublic": GastoDiarioPublic,
    "CreditoDeudaPublic": CreditoDeudaPublic,
}

UsuarioNested.model_rebuild(_types_namespace=_types_namespace)
CuentaNested.model_rebuild(_types_namespace=_types_namespace)
IngresoNested.model_rebuild(_types_namespace=_types_namespace)
GastoFijoNested.model_rebuild(_types_namespace=_types_namespace)
GastoDiarioNested.model_rebuild(_types_namespace=_types_namespace)
CreditoDeudaNested.model_rebuild(_types_namespace=_types_namespace)


__all__ = [
    "CreditoDeuda",
    "CreditoDeudaBase",
    "CreditoDeudaNested",
    "CreditoDeudaPublic",
    "Cuenta",
    "CuentaBase",
    "CuentaNested",
    "CuentaPublic",
    "GastoDiario",
    "GastoDiarioBase",
    "GastoDiarioNested",
    "GastoDiarioPublic",
    "GastoFijo",
    "GastoFijoBase",
    "GastoFijoNested",
    "GastoFijoPublic",
    "Ingreso",
    "IngresoBase",
    "IngresoNested",
    "IngresoPublic",
    "Usuario",
    "UsuarioBase",
    "UsuarioNested",
    "UsuarioPublic",
]
