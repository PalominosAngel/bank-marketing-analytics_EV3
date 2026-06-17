"""Dashboard principal diferenciado por audiencia."""
from __future__ import annotations

import streamlit as st
import requests

import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go


# ---------------------------------------------------------------------
# Tema global Plotly: mejora contraste de todos los gráficos del dashboard
# ---------------------------------------------------------------------
pio.templates["bank_light"] = go.layout.Template(
    layout=dict(
        font=dict(color="#111827", size=14),
        title=dict(font=dict(color="#111827", size=20)),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis=dict(
            title=dict(font=dict(color="#111827")),
            tickfont=dict(color="#111827"),
            gridcolor="#E5E7EB",
            zerolinecolor="#D1D5DB",
            linecolor="#9CA3AF",
        ),
        yaxis=dict(
            title=dict(font=dict(color="#111827")),
            tickfont=dict(color="#111827"),
            gridcolor="#E5E7EB",
            zerolinecolor="#D1D5DB",
            linecolor="#9CA3AF",
        ),
        legend=dict(
            font=dict(color="#111827"),
            title=dict(font=dict(color="#111827")),
        ),
        coloraxis_colorbar=dict(
            title=dict(font=dict(color="#111827")),
            tickfont=dict(color="#111827"),
        ),
    )
)

pio.templates.default = "bank_light"
px.defaults.template = "bank_light"


def aplicar_tema_plotly(fig):
    """Aplica contraste visual a cualquier figura Plotly antes de mostrarla."""
    fig.update_layout(
        template="bank_light",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="#111827", size=14),
        title_font=dict(color="#111827", size=20),
        legend=dict(
            font=dict(color="#111827"),
            title=dict(font=dict(color="#111827")),
        ),
        coloraxis_colorbar=dict(
            title=dict(font=dict(color="#111827")),
            tickfont=dict(color="#111827"),
        ),
    )

    fig.update_xaxes(
        title_font=dict(color="#111827"),
        tickfont=dict(color="#111827"),
        gridcolor="#E5E7EB",
        zerolinecolor="#D1D5DB",
        linecolor="#9CA3AF",
    )

    fig.update_yaxes(
        title_font=dict(color="#111827"),
        tickfont=dict(color="#111827"),
        gridcolor="#E5E7EB",
        zerolinecolor="#D1D5DB",
        linecolor="#9CA3AF",
    )

    return fig


# ---------------------------------------------------------------------
# Parche global para st.plotly_chart:
# cada gráfico que se dibuje será corregido automáticamente.
# ---------------------------------------------------------------------
_original_plotly_chart = st.plotly_chart


def plotly_chart_con_tema(fig, *args, **kwargs):
    try:
        fig = aplicar_tema_plotly(fig)
    except Exception:
        pass
    return _original_plotly_chart(fig, *args, **kwargs)


st.plotly_chart = plotly_chart_con_tema


from dashboards.pages import executive, operational, technical
from dashboards.data_access import get_json


st.set_page_config(page_title="Bank Marketing Analytics", page_icon="📊", layout="wide")
st.title("Bank Marketing Analytics")
st.markdown("Plataforma analítica para campañas bancarias y segmentación de clientes.")

try:
    get_json("/health")
except requests.RequestException as exc:
    st.error("La API propia no está disponible. Ejecuta primero el pipeline y levanta FastAPI.")
    st.code(
        "python -m etl.pipeline\n"
        "uvicorn api.main:app --reload\n"
        "PYTHONPATH=. streamlit run dashboards/app.py"
    )
    st.exception(exc)
    st.stop()

view = st.sidebar.radio("Selecciona la audiencia", ["Ejecutiva", "Operativa", "Técnica"])
st.sidebar.markdown("---")
st.sidebar.caption("Fuente principal: bank.csv · API externa: World Bank · Persistencia: SQL")

if view == "Ejecutiva":
    executive.render()
elif view == "Operativa":
    operational.render()
else:
    technical.render()