# 5palPeso — API REST de Finanzas Personales

[![FastAPI Cloud](https://img.shields.io/badge/FastAPI_Cloud-Deployed-009688?style=flat&logo=fastapi)](https://efi-backend.fastapicloud.dev/docs)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python)](https://www.python.org/)
[![SQLModel](https://img.shields.io/badge/SQLModel-SQLite-blue?style=flat)](https://sqlmodel.tiangolo.com/)

Backend modular desarrollado para la **Evaluación Final Integradora (EFI) 2026** del espacio curricular **Práctica Profesionalizante I: Python**, Tecnicatura Superior en Desarrollo de Software — **ITEC Río Cuarto**.

- **Docente:** Prof. Facundo Esteban Lemo
- **Integrantes:** Facundo Giacri & Valentín Pomilio
- **API en Producción (Cloud):** [https://efi-backend.fastapicloud.dev](https://efi-backend.fastapicloud.dev)
- **Documentación Interactiva (Swagger / OpenAPI):** [https://efi-backend.fastapicloud.dev/docs](https://efi-backend.fastapicloud.dev/docs)
- **Frontend Asociado (Vercel):** [https://efi-frontend-5pal-peso.vercel.app](https://efi-frontend-5pal-peso.vercel.app)

---

## 📌 Visión del Negocio y Dominio Financiero

El sistema gestiona el flujo de fondos según el ciclo real de ingresos del usuario (determinado por su `dia_cobro`), descontando compromisos ineludibles y protegiendo el ahorro antes de definir el ritmo de gasto diario disponible.

### Funcionalidades y Reglas de Negocio Clave
1. **Ciclo Financiero Dinámico:** Sincronizado por el día de cobro del usuario (desde el día `dia_cobro` del mes actual hasta el día previo al próximo cobro).
2. **Máquina de Estados de la Deuda:** Los créditos se amortizan cuota a cuota (`POST /creditos/{id}/registrar-pago`) transicionando automáticamente a `finalizada` al cancelar la última cuota, liberando capacidad de endeudamiento.
3. **Baja Lógica de Gastos Fijos:** Los compromisos cancelados (`activo: bool`) no se eliminan físicamente para preservar los balances históricos de ciclos anteriores.
4. **Sugerencia de Distribución de Fondos (Cash Allocation):** Sugiere qué monto retener en cada cuenta bancaria o billetera para evitar rebotes de débitos automáticos.
5. **Simulador de Crédito (What-If):** Proyecta mes a mes el impacto que tendría asumir una nueva deuda sobre la liquidez diaria y el índice de endeudamiento (DTI).
6. **Database Seeding Automático:** Al iniciar el servidor en un entorno vacío, un seeder idempotente en el `lifespan` de FastAPI puebla la base de datos con datos realistas para demostración y evaluación.

---

## 🏛️ Estructura de Endpoints (Path Operations)

- **Usuarios (`/usuarios`):** CRUD completo y consulta de usuario anidado con sus entidades.
- **Cuentas Financieras (`/cuentas`):** Bancos, billeteras virtuales y efectivo.
- **Ingresos (`/ingresos`):** Registro de sueldos y cobros recurrentes u ocasionales.
- **Gastos Fijos (`/gastos-fijos`):** Servicios, alquileres y suscripciones con fecha de vencimiento y baja lógica.
- **Créditos y Deudas (`/creditos`):** Préstamos, compras en cuotas fijas, cálculo de CFT y registro de pago atómico de cuotas.
- **Gastos Diarios (`/gastos-diarios`):** Gastos de consumo corriente vinculados al ciclo activo.
- **Métricas y Análisis (`/metricas`):**
  - `GET /metricas/ciclo-actual/{usuario_id}` : Superávit operativo, saldo libre y presupuesto diario dinámico.
  - `GET /metricas/distribucion-fondos/{usuario_id}` : Fondos sugeridos a retener por cuenta.
  - `POST /metricas/simulacion/credito/{usuario_id}` : Proyección mensual con amortización temporal.

---

## 🛠️ Stack Tecnológico

- **FastAPI** (`fastapi[standard]`)
- **SQLModel** (ORM que combina SQLAlchemy + Pydantic v2)
- **SQLite**
- **Alembic** (gestión de migraciones)
- **FastAPI-Pagination** (paginación declarativa de colecciones)
- **Uvicorn** (servidor ASGI)

---

## 🚀 Instalación y Ejecución Local

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/cachu94/efi-backend-misfinanzas.git
   cd efi-backend-misfinanzas
   ```

2. **Crear y activar entorno virtual:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Linux/macOS
   .venv\Scripts\activate     # En Windows
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   # O utilizando uv:
   # uv sync
   ```

4. **Ejecutar el servidor en modo desarrollo:**
   ```bash
   fastapi dev src/main.py
   # O con uvicorn:
   # uvicorn src.main:app --reload
   ```

5. **Acceder a la documentación Swagger:**
   Abrir [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
