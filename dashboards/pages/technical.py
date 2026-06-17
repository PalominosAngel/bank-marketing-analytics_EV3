from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboards.data_access import get_json


def render() -> None:
    st.header("Vista técnica")
    st.caption("Calidad de datos, trazabilidad del ETL y segmentación exploratoria.")

    quality = pd.DataFrame(get_json("/api/data-quality"))
    runs = pd.DataFrame(get_json("/api/etl-runs"))
    segments = pd.DataFrame(get_json("/api/segments"))
    customers = pd.DataFrame(get_json("/api/customers", {"limit": 5000}))

    st.subheader("Estado de calidad")
    st.dataframe(quality, use_container_width=True)

    st.subheader("Historial de ejecuciones ETL")
    st.dataframe(runs, use_container_width=True)

    st.subheader("Resumen de segmentos K-Means")
    st.dataframe(segments, use_container_width=True)

    fig_pca = px.scatter(
        customers, x="pca_component_1", y="pca_component_2", color="customer_segment",
        hover_data=["age", "balance", "job", "conversion_flag"], opacity=0.7,
        title="PCA en dos dimensiones para visualizar segmentos K-Means",
        labels={"pca_component_1": "Componente principal 1", "pca_component_2": "Componente principal 2", "customer_segment": "Segmento"},
    )
    fig_pca.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig_pca, use_container_width=True)

    numeric_columns = ["age", "balance", "duration", "campaign", "pdays", "previous", "conversion_flag"]
    correlation = customers[numeric_columns].corr().round(2)
    fig_corr = px.imshow(
        correlation, text_auto=True, aspect="auto",
        title="Matriz de correlación de variables numéricas",
        labels={"color": "Correlación"},
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    st.info("La segmentación es exploratoria. Su objetivo es apoyar el análisis descriptivo, no reemplazar el criterio comercial ni predecir causalidad.")
