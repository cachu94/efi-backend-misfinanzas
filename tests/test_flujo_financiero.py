from datetime import date

from fastapi.testclient import TestClient


def test_flujo_financiero(client: TestClient):
    # 1. Health check
    res = client.get("/")
    assert res.status_code == 200

    # 2. Crear usuario
    user_data = {
        "nombre": " Facu Lemo",
        "email": "facu.lemo@example.com",
        "dia_cobro": 15,
        "porcentaje_ahorro": 20.0,
    }

    res_user = client.post("/usuarios/", json=user_data)
    assert res_user.status_code == 201
    user = res_user.json()
    user_id = user["id"]

    # 3. Crear Cuenta Bancaria
    cuenta_data = {
        "usuario_id": user_id,
        "nombre": "ICBC Sueldo",
        "tipo_cuenta": "banco",
        "entidad": "Banco ICBC",
    }
    res_cuenta = client.post("/cuentas/", json=cuenta_data)
    assert res_cuenta.status_code == 201
    cuenta_id = res_cuenta.json()["id"]

    # 4. Crear Ingreso
    ingreso_data = {
        "usuario_id": user_id,
        "cuenta_id": cuenta_id,
        "descripcion": "Sueldo Mensual",
        "monto": 1000000.0,
        "fecha_ingreso": str(date.today()),
        "es_recurrente": True,
    }
    res_ingreso = client.post("/ingresos/", json=ingreso_data)
    assert res_ingreso.status_code == 201

    # 5. Crear Gasto Fijo
    gasto_fijo_data = {
        "usuario_id": user_id,
        "cuenta_id": cuenta_id,
        "categoria": "Suscripción",
        "descripcion": "Netflix",
        "monto": 20000.0,
        "dia_vencimiento": 10,
    }
    res_gf = client.post("/gastos-fijos/", json=gasto_fijo_data)
    assert res_gf.status_code == 201

    # 6. Crear Crédito y Registrar Pago (Máquina de estados)
    credito_data = {
        "usuario_id": user_id,
        "cuenta_id": cuenta_id,
        "entidad_acreedora": "Mercado Pago",
        "descripcion": "Préstamo Personal",
        "monto_cuota": 100000.0,
        "total_cuotas": 2,
        "cuota_actual": 1,
        "fecha_inicio": str(date.today()),
    }
    res_credito = client.post("/creditos/", json=credito_data)
    assert res_credito.status_code == 201
    credito_id = res_credito.json()["id"]
    assert res_credito.json()["estado"] == "activo"

    # Pagamos la cuota final (debe mutar a finalizada)
    res_pago = client.post(f"/creditos/{credito_id}/registrar-pago")
    assert res_pago.status_code == 200
    assert res_pago.json()["cuota_actual"] == 2
    assert res_pago.json()["estado"] == "finalizada"

    # 7. Probar Métricas de Ciclo Actual
    res_metricas = client.get(f"/metricas/ciclo-actual/{user_id}")
    assert res_metricas.status_code == 200
    metricas = res_metricas.json()
    assert metricas["ingresos_totales"] == 1000000.0
    assert metricas["gastos_fijos_totales"] == 20000.0
    assert metricas["ahorro_programado"] == 200000.0  # 20% de 1.000.000
    assert metricas["presupuesto_diario_dinamico"] > 0

    # 8. Probar Simulación What-If
    simulacion_data = {
        "monto_cuota_simulada": 50000.0,
        "total_cuotas_simuladas": 6,
    }
    res_sim = client.post(
        f"/metricas/simulacion/credito/{user_id}", json=simulacion_data
    )
    assert res_sim.status_code == 200
    assert len(res_sim.json()) == 6
