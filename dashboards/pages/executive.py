from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboards.data_access import get_json


def render() -> None:
    st.header("Vista ejecutiva")
    st.caption("Indicadores de campaña orientados a decisiones comerciales.")

    kpis = get_json("/api/kpis")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clientes contactados", f"{int(kpis['total_customers']):,}".replace(",", "."))
    c2.metric("Conversiones", f"{int(kpis['conversions']):,}".replace(",", "."))
    c3.metric("Tasa de conversión", f"{kpis['conversion_rate_pct']:.2f}%")
    c4.metric("Saldo promedio", f"€ {kpis['average_balance']:,.0f}".replace(",", "."))

    customers = pd.DataFrame(get_json("/api/customers", {"limit": 5000}))
    by_job = (
        customers.groupby("job", as_index=False)
        .agg(customers=("customer_id", "count"), conversion_rate=("conversion_flag", "mean"))
        .assign(conversion_rate=lambda df: (df["conversion_rate"] * 100).round(2))
        .sort_values("conversion_rate", ascending=False)
    )
    fig_job = px.bar(
        by_job, x="conversion_rate", y="job", orientation="h", text="conversion_rate",
        title="Tasa de conversión por ocupación: perfiles con mejor respuesta",
        labels={"conversion_rate": "Conversión (%)", "job": "Ocupación"},
    )
    fig_job.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig_job.update_layout(plot_bgcolor="white", paper_bgcolor="white", yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_job, use_container_width=True)

    monthly = (
        customers.groupby(["month_number", "month"], as_index=False)
        .agg(customers=("customer_id", "count"), conversion_rate=("conversion_flag", "mean"))
        .assign(conversion_rate=lambda df: (df["conversion_rate"] * 100).round(2))
        .sort_values("month_number")
    )
    fig_month = px.line(
        monthly, x="month", y="conversion_rate", markers=True,
        title="Evolución mensual de la conversión de campañas",
        labels={"month": "Mes", "conversion_rate": "Conversión (%)"},
    )
    fig_month.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig_month, use_container_width=True)

    macro = pd.DataFrame(get_json("/api/economic-indicators"))
    if not macro.empty:
        fig_macro = px.line(
            macro, x="year", y="value", color="indicator_name", markers=True,
            title="Contexto macroeconómico de Portugal obtenido desde API externa",
            labels={"year": "Año", "value": "Valor", "indicator_name": "Indicador"},
        )
        fig_macro.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_macro, use_container_width=True)
        st.caption("Los indicadores económicos contextualizan la campaña; no se interpretan como causa directa de la conversión.")
