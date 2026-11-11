from datetime import date, timedelta

from sqlmodel import Session

from src.models import CreditoDeuda, Cuenta, GastoDiario, GastoFijo, Ingreso, Usuario


def sembrar_datos_iniciales(db: Session):
    hoy = date.today()

    # 1. Usuario Principal
    usuario = Usuario(
        nombre="Facundo",
        email="facundo@example.com",
        dia_cobro=15,
        porcentaje_ahorro=10.0,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    # 2. Cuentas Financieras
    cuenta_banco = Cuenta(
        usuario_id=usuario.id,
        nombre="ICBC Sueldo",
        entidad="ICBC",
        tipo_cuenta="banco",
    )
    cuenta_mp = Cuenta(
        usuario_id=usuario.id,
        nombre="Mercado Pago",
        entidad="Mercado Pago",
        tipo_cuenta="billetera_virtual",
    )
    db.add_all([cuenta_banco, cuenta_mp])
    db.commit()
    db.refresh(cuenta_banco)
    db.refresh(cuenta_mp)

    # 3. Ingreso del Ciclo
    ingreso = Ingreso(
        usuario_id=usuario.id,
        cuenta_id=cuenta_banco.id,
        descripcion="Sueldo en Blanco",
        monto=1500000.0,
        fecha_ingreso=hoy - timedelta(days=2),
        es_recurrente=True,
    )
    db.add(ingreso)

    # 4. Gastos Fijos
    alquiler = GastoFijo(
        usuario_id=usuario.id,
        cuenta_id=cuenta_banco.id,
        descripcion="Alquiler Depto",
        categoria="Vivienda",
        monto=350000.0,
        dia_vencimiento=10,
    )
    internet = GastoFijo(
        usuario_id=usuario.id,
        cuenta_id=cuenta_banco.id,
        descripcion="Fibertel 300MB",
        categoria="Servicios",
        monto=28000.0,
        dia_vencimiento=15,
    )
    netflix = GastoFijo(
        usuario_id=usuario.id,
        cuenta_id=cuenta_mp.id,
        descripcion="Netflix Premium",
        categoria="Suscripciones",
        monto=9500.0,
        dia_vencimiento=20,
    )
    db.add_all([alquiler, internet, netflix])
    # 5. Créditos / Deudas Activas
    auto = CreditoDeuda(
        usuario_id=usuario.id,
        cuenta_id=cuenta_banco.id,
        entidad_acreedora="Autocity",
        descripcion="Plan de Ahorro FIAT Mobi",
        monto_cuota=500000.0,
        total_cuotas=84,
        cuota_actual=26,
        fecha_inicio=date(2024, 12, 23),
        precio_contado=30000000.0,
    )
    notebook = CreditoDeuda(
        usuario_id=usuario.id,
        cuenta_id=cuenta_mp.id,
        entidad_acreedora="Banco Galicia",
        descripcion="Notebook Lenovo 12 cuotas",
        monto_cuota=65000.0,
        total_cuotas=12,
        cuota_actual=3,
        fecha_inicio=date(2026, 8, 15),
        precio_contado=650000.0,
    )
    db.add_all([auto, notebook])
    # 6. Gastos Diarios de prueba
    g1 = GastoDiario(
        usuario_id=usuario.id,
        cuenta_id=cuenta_mp.id,
        notas="Supermercado ChangoMás",
        monto=45000.0,
        categoria="Supermercado",
        fecha=hoy - timedelta(days=1),
    )
    g2 = GastoDiario(  # pyright: ignore[reportUndefinedVariable]
        usuario_id=usuario.id,
        cuenta_id=cuenta_banco.id,
        notas="Carga Combustible YPF",
        monto=25000.0,
        categoria="Transporte",
        fecha=hoy,
    )
    db.add_all([g1, g2])
    db.commit()
