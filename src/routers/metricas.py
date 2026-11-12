from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from src.database import get_session
from src.models import CreditoDeuda, Cuenta, GastoDiario, GastoFijo, Ingreso, Usuario
from src.models.metricas import (
    ItemProyeccionMes,
    MetricasCicloResponse,
    SimulacionCreditoRequest,
    SugerenciaDistribucionCuenta,
)

router = APIRouter(prefix="/metricas", tags=["Métricas y Análisis Financiero"])

error_usuario_404 = {
    404: {
        "description": "Usuario no encontrado",
        "content": {
            "application/json": {"example": {"detail": "Usuario no encontrado!"}}
        },
    }
}


def obtener_rango_ciclo(
    dia_cobro: int,
    fecha_ref: date = date.today(),  # noqa: B008
) -> tuple[date, date]:
    year = fecha_ref.year
    month = fecha_ref.month

    if fecha_ref.day >= dia_cobro:
        inicio = date(year, month, dia_cobro)
        # Siguiente mes
        if month == 12:
            siguiente_mes = date(year + 1, 1, dia_cobro)
        else:
            siguiente_mes = date(year, month + 1, dia_cobro)
    else:
        # Mes anterior
        if month == 1:
            inicio = date(year - 1, 12, dia_cobro)
        else:
            inicio = date(year, month - 1, dia_cobro)
        siguiente_mes = date(year, month, dia_cobro)

    fin = siguiente_mes - timedelta(days=1)
    return inicio, fin


@router.get(
    "/ciclo-actual/{usuario_id}",
    response_model=MetricasCicloResponse,
    responses=error_usuario_404,  # type: ignore
)
def obtener_metricas_ciclo(usuario_id: int, db: Session = Depends(get_session)):  # noqa: B008
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado!"
        )

    hoy = date.today()
    inicio_ciclo, fin_ciclo = obtener_rango_ciclo(usuario.dia_cobro, hoy)

    dias_restantes = max((fin_ciclo - hoy).days + 1, 1)

    ingresos = db.exec(
        select(Ingreso).where(
            Ingreso.usuario_id == usuario_id,
            Ingreso.fecha_ingreso >= inicio_ciclo,
            Ingreso.fecha_ingreso <= fin_ciclo,
        )
    ).all()
    ingresos_totales = sum(i.monto for i in ingresos)

    gastos_fijos = db.exec(
        select(GastoFijo).where(
            GastoFijo.usuario_id == usuario_id,
            GastoFijo.activo == True,
        )
    ).all()
    gastos_fijos_totales = sum(gf.monto for gf in gastos_fijos)

    creditos = db.exec(
        select(CreditoDeuda).where(
            CreditoDeuda.usuario_id == usuario_id,
            CreditoDeuda.estado == "activo",
        )
    ).all()
    cuotas_deudas_totales = sum(c.monto_cuota for c in creditos)

    superavit_operativo = ingresos_totales - (
        gastos_fijos_totales + cuotas_deudas_totales
    )
    ahorro_programado = ingresos_totales * (usuario.porcentaje_ahorro / 100.0)
    saldo_libre_ciclo = superavit_operativo - ahorro_programado

    gastos_diarios = db.exec(
        select(GastoDiario).where(
            GastoDiario.usuario_id == usuario_id,
            GastoDiario.fecha >= inicio_ciclo,
            GastoDiario.fecha <= fin_ciclo,
        )
    ).all()
    gastos_diarios_acumulados = sum(gd.monto for gd in gastos_diarios)

    saldo_disponible_remanente = saldo_libre_ciclo - gastos_diarios_acumulados
    presupuesto_diario_dinamico = max(saldo_disponible_remanente / dias_restantes, 0.0)

    return MetricasCicloResponse(
        periodo_inicio=inicio_ciclo,
        periodo_fin=fin_ciclo,
        dias_restantes=dias_restantes,
        ingresos_totales=ingresos_totales,
        gastos_fijos_totales=gastos_fijos_totales,
        cuotas_deudas_totales=cuotas_deudas_totales,
        superavit_operativo=superavit_operativo,
        ahorro_programado=ahorro_programado,
        saldo_libre_ciclo=saldo_libre_ciclo,
        gastos_diarios_acumulados=gastos_diarios_acumulados,
        saldo_disponible_remanente=saldo_disponible_remanente,
        presupuesto_diario_dinamico=round(presupuesto_diario_dinamico, 2),
    )


@router.get(
    "/distribucion-fondos/{usuario_id}",
    response_model=list[SugerenciaDistribucionCuenta],
    responses=error_usuario_404,  # type: ignore
)
def obtener_distribucion_fondos(usuario_id: int, db: Session = Depends(get_session)):  # noqa: B008
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado!"
        )

    gastos_fijos = db.exec(
        select(GastoFijo).where(
            GastoFijo.usuario_id == usuario_id, GastoFijo.activo == True
        )
    ).all()

    creditos = db.exec(
        select(CreditoDeuda).where(
            CreditoDeuda.usuario_id == usuario_id, CreditoDeuda.estado == "activo"
        )
    ).all()

    distribucion: dict[int | None, float] = {}

    for gf in gastos_fijos:
        distribucion[gf.cuenta_id] = distribucion.get(gf.cuenta_id, 0.0) + gf.monto

    for c in creditos:
        distribucion[c.cuenta_id] = distribucion.get(c.cuenta_id, 0.0) + c.monto_cuota

    resultado = []
    for cuenta_id, monto in distribucion.items():
        if cuenta_id:
            cuenta = db.get(Cuenta, cuenta_id)
            nombre = cuenta.nombre if cuenta else f"Cuenta ID {cuenta_id}"
        else:
            nombre = "Sin cuenta asignada"

        resultado.append(
            SugerenciaDistribucionCuenta(
                cuenta_id=cuenta_id,
                nombre_cuenta=nombre,
                monto_comprometido=monto,
                motivo=f"Retener ${monto:.2f} para cubrir débitos automáticos y cuotas fijas.",
            )
        )

    return resultado


@router.post(
    "/simulacion/credito/{usuario_id}",
    response_model=list[ItemProyeccionMes],
    responses=error_usuario_404,  # type: ignore
)
def simular_nuevo_credito(
    usuario_id: int,
    simulacion: SimulacionCreditoRequest,
    db: Session = Depends(get_session),  # noqa: B008
):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado!"
        )

    hoy = date.today()
    inicio_ciclo, _ = obtener_rango_ciclo(usuario.dia_cobro, hoy)

    ingresos = db.exec(select(Ingreso).where(Ingreso.usuario_id == usuario_id)).all()
    ingreso_base = sum(i.monto for i in ingresos) or 1.0

    gastos_fijos = db.exec(
        select(GastoFijo).where(
            GastoFijo.usuario_id == usuario_id, GastoFijo.activo == True
        )
    ).all()
    gasto_fijo_base = sum(gf.monto for gf in gastos_fijos)

    creditos_activos = db.exec(
        select(CreditoDeuda).where(
            CreditoDeuda.usuario_id == usuario_id, CreditoDeuda.estado == "activo"
        )
    ).all()

    proyeccion = []

    for mes in range(1, simulacion.total_cuotas_simuladas + 1):
        cuotas_existentes_mes = 0.0
        for c in creditos_activos:
            cuotas_restantes = c.total_cuotas - c.cuota_actual + 1
            if mes <= cuotas_restantes:
                cuotas_existentes_mes += c.monto_cuota

        deuda_total_mes = cuotas_existentes_mes + simulacion.monto_cuota_simulada
        ahorro = ingreso_base * (usuario.porcentaje_ahorro / 100.0)
        superavit = ingreso_base - gasto_fijo_base - deuda_total_mes - ahorro
        presupuesto_diario = max(superavit / 30.0, 0.0)

        dti = (deuda_total_mes / ingreso_base) * 100.0

        proyeccion.append(
            ItemProyeccionMes(
                mes_numero=mes,
                fecha_referencia=inicio_ciclo + timedelta(days=30 * (mes - 1)),
                cuotas_existentes=cuotas_existentes_mes,
                cuota_simulada=simulacion.monto_cuota_simulada,
                superavit_estimado=round(superavit, 2),
                presupuesto_diario_estimado=round(presupuesto_diario, 2),
                indice_endeudamiento_dti=round(dti, 2),
            )
        )

    return proyeccion
