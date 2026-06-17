from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboards.data_access import get_json


def render() -> None:
    st.header("Vista operativa")
    st.caption("Exploración de clientes y canales para planificar campañas.")
    customers = pd.DataFrame(get_json("/api/customers", {"limit": 5000}))

    jobs = ["Todos"] + sorted(customers["job"].dropna().unique().tolist())
    segments = ["Todos"] + sorted(customers["customer_segment"].dropna().astype(int).unique().tolist())
    c1, c2, c3 = st.columns(3)
    selected_job = c1.selectbox("Ocupación", jobs)
    selected_segment = c2.selectbox("Segmento", segments)
    only_converted = c3.checkbox("Mostrar solo conversiones")

    filtered = customers.copy()
    if selected_job != "Todos":
        filtered = filtered[filtered["job"] == selected_job]
    if selected_segment != "Todos":
        filtered = filtered[filtered["customer_segment"] == int(selected_segment)]
    if only_converted:
        filtered = filtered[filtered["conversion_flag"] == 1]

    st.metric("Clientes visibles con los filtros aplicados", len(filtered))

    by_channel = (
        filtered.groupby("channel_label", as_index=False)
        .agg(customers=("customer_id", "count"), conversion_rate=("conversion_flag", "mean"))
        .assign(conversion_rate=lambda df: (df["conversion_rate"] * 100).round(2))
        .sort_values("conversion_rate", ascending=False)
    )
    fig_channel = px.bar(
        by_channel, x="channel_label", y="conversion_rate", text="conversion_rate",
        title="Rendimiento por canal de contacto",
        labels={"channel_label": "Canal", "conversion_rate": "Conversión (%)"},
    )
    fig_channel.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig_channel.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig_channel, use_container_width=True)

    fig_duration = px.histogram(
        filtered, x="duration_minutes", nbins=30, color="y",
        title="Distribución de duración de llamadas según resultado",
        labels={"duration_minutes": "Duración de llamada (min)", "count": "Clientes", "y": "Resultado"},
    )
    fig_duration.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig_duration, use_container_width=True)

    st.subheader("Muestra descargable")
    visible_columns = [
        "customer_id", "age", "job", "education", "balance", "housing", "loan",
        "channel_label", "duration_minutes", "campaign", "customer_segment", "y"
    ]
    st.dataframe(filtered[visible_columns], use_container_width=True, height=360)
    st.download_button(
        "Descargar muestra filtrada en CSV",
        data=filtered[visible_columns].to_csv(index=False).encode("utf-8"),
        file_name="clientes_filtrados.csv",
        mime="text/csv",
    )
