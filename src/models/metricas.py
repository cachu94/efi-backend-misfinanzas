from datetime import date

from pydantic import BaseModel, Field


class MetricasCicloResponse(BaseModel):
    periodo_inicio: date
    periodo_fin: date
    dias_restantes: int
    ingresos_totales: float
    gastos_fijos_totales: float
    cuotas_deudas_totales: float
    superavit_operativo: float
    ahorro_programado: float
    saldo_libre_ciclo: float
    gastos_diarios_acumulados: float
    saldo_disponible_remanente: float
    presupuesto_diario_dinamico: float


class SugerenciaDistribucionCuenta(BaseModel):
    cuenta_id: int | None
    nombre_cuenta: str
    monto_comprometido: float
    motivo: str


class SimulacionCreditoRequest(BaseModel):
    monto_cuota_simulada: float = Field(
        gt=0, description="Monto mensual de la nueva cuota"
    )
    total_cuotas_simuladas: int = Field(
        ge=1, description="Cantidad de cuotas a simular"
    )


class ItemProyeccionMes(BaseModel):
    mes_numero: int
    fecha_referencia: date
    cuotas_existentes: float
    cuota_simulada: float
    superavit_estimado: float
    presupuesto_diario_estimado: float
    indice_endeudamiento_dti: float
