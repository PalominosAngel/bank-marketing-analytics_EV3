"""Segmentación exploratoria de clientes mediante K-Means y PCA."""
from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


CLUSTER_FEATURES = ["age", "balance", "duration", "campaign", "pdays_for_model", "previous"]


@dataclass
class ClusteringMetadata:
    features: list[str]
    n_clusters: int
    explained_variance_pc1: float
    explained_variance_pc2: float
    inertia: float
    random_state: int


def add_customer_segments(df: pd.DataFrame, output_metadata_path: Path, n_clusters: int = 4) -> pd.DataFrame:
    """Añade cluster y coordenadas PCA a cada cliente.

    El análisis es exploratorio y sirve para apoyar la interpretación comercial;
    no representa una predicción causal ni una recomendación automática.
    """
    if len(df) < n_clusters:
        raise ValueError("No existen suficientes filas para aplicar K-Means")

    result = df.copy()
    model_frame = result[CLUSTER_FEATURES].fillna(0).astype(float)
    scaled = StandardScaler().fit_transform(model_frame)

    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(scaled)

    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    result["customer_segment"] = model.fit_predict(scaled).astype(int)
    result["pca_component_1"] = coords[:, 0]
    result["pca_component_2"] = coords[:, 1]

    metadata = ClusteringMetadata(
        features=CLUSTER_FEATURES,
        n_clusters=n_clusters,
        explained_variance_pc1=float(pca.explained_variance_ratio_[0]),
        explained_variance_pc2=float(pca.explained_variance_ratio_[1]),
        inertia=float(model.inertia_),
        random_state=42,
    )
    output_metadata_path.parent.mkdir(parents=True, exist_ok=True)
    output_metadata_path.write_text(json.dumps(asdict(metadata), ensure_ascii=False, indent=2), encoding="utf-8")
    return result
