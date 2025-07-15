import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Simulador Reforma Laboral", layout="centered")
st.title("💼 Simulador de Costos Laborales - Planta 24/7")

st.markdown("""
Este simulador estima el **incremento mensual en costos de operación** de una planta 24/7 debido a la reforma laboral (Colombia) entre 2025 y 2027.

Los cambios considerados son:

- 📉 Reducción de la jornada ordinaria: **46 h → 44 h semanales (julio 2025)**
- 🌙 Recargo nocturno desde las **7 p.m.** (diciembre 2025)
- 📆 Aumento progresivo de recargos dominicales/festivos:
    - 80% desde julio 2025
    - 90% desde julio 2026
    - 100% desde julio 2027
""")

with st.form("formulario"):
    st.subheader("🔧 Parámetros de operación")
    valor_hora = st.number_input("Valor hora ordinaria ($)", value=5000.0, step=100.0)
    empleados_turno = st.number_input("Número de empleados por turno", value=6, step=1)
    turnos_dia = st.number_input("Turnos diarios", value=3, step=1)
    fecha_inicio = st.date_input("Fecha de inicio", value=datetime(2025, 7, 1))
    fecha_fin = st.date_input("Fecha de fin", value=datetime(2027, 12, 31))

    submitted = st.form_submit_button("Simular")

if submitted and fecha_inicio < fecha_fin:
    dias = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='D')
    resultados = []

    for fecha in dias:
        año, mes = fecha.year, fecha.month
        dia_semana = fecha.weekday()

        # Ajustes según la fecha
        jornada_semanal = 46 if fecha < datetime(2025, 7, 1) else 44
        horas_dia = 24
        horas_semanales_total = 168  # 24 * 7

        # Recargo dominical
        if fecha < datetime(2025, 7, 1):
            recargo_domi = 0.75
        elif fecha < datetime(2026, 7, 1):
            recargo_domi = 0.80
        elif fecha < datetime(2027, 7, 1):
            recargo_domi = 0.90
        else:
            recargo_domi = 1.00

        # Recargo nocturno desde 7 p.m. (diciembre 2025)
        nocturno_inicio = 21 if fecha < datetime(2025, 12, 1) else 19
        horas_nocturnas = 24 - nocturno_inicio

        # Cálculo para el día
        horas_diurnas = 24 - horas_nocturnas
        horas_domingo = 24 if dia_semana == 6 else 0

        costo_dia = 0
        # Horas ordinarias (primeras jornada_semanal/7 por día)
        horas_ord = jornada_semanal / 7
        horas_extra = max(0, horas_diurnas - horas_ord)
        empleados = empleados_turno * turnos_dia

        valor_dia = (
            horas_ord * valor_hora +
            horas_extra * valor_hora * 1.25 +
            horas_nocturnas * valor_hora * 0.35 +
            horas_domingo * valor_hora * recargo_domi
        ) * empleados

        resultados.append({
            "fecha": fecha,
            "costo_diario": valor_dia
        })

    df = pd.DataFrame(resultados)
    df["mes"] = df["fecha"].dt.to_period("M")
    resumen = df.groupby("mes").sum().reset_index()
    resumen["mes"] = resumen["mes"].astype(str)

    st.subheader("📊 Costo mensual total")
    st.dataframe(resumen.rename(columns={"costo_diario": "Costo mensual ($)"}), use_container_width=True)

    st.line_chart(resumen.set_index("mes"), y="costo_diario", use_container_width=True)

    st.success("✅ Simulación completada")

elif submitted:
    st.error("⚠️ La fecha de inicio debe ser anterior a la fecha de fin.")
