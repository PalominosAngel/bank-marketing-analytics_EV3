"""Clasificación supervisada: predice si el cliente contrata el depósito a plazo.

La columna `duration` (duración de la llamada) se excluye deliberadamente del set
de features: solo se conoce una vez realizada la llamada (si dura 0, `y` es
necesariamente "no"), por lo que usarla como predictor introduce fuga de
información (data leakage) y produce un modelo que no sirve para decidir a quién
llamar de antemano. Ver docs/decisiones_tecnicas.md para el detalle y la fuente
que documenta este comportamiento en el dataset UCI Bank Marketing original.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TARGET_COLUMN = "conversion_flag"
NUMERIC_FEATURES = ["age", "balance", "day", "campaign", "pdays", "previous"]
CATEGORICAL_FEATURES = [
    "job", "marital", "education", "default", "housing", "loan", "contact", "month", "poutcome",
]
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES
EXCLUDED_LEAKAGE_FEATURES = ["duration", "duration_minutes"]

RANDOM_STATE = 42
TEST_SIZE = 0.25
CV_FOLDS = 3


@dataclass
class ModelResult:
    name: str
    best_params: dict
    cv_best_roc_auc: float
    test_roc_auc: float
    test_accuracy: float
    classification_report: dict
    confusion_matrix: list
    interpretability: list
    pipeline: Pipeline = field(repr=False)


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )


def _train_logistic(X_train: pd.DataFrame, y_train: pd.Series) -> GridSearchCV:
    pipeline = Pipeline([
        ("preprocess", build_preprocessor()),
        ("model", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE)),
    ])
    grid = GridSearchCV(
        pipeline,
        param_grid={"model__C": [0.1, 1.0, 10.0]},
        scoring="roc_auc",
        cv=CV_FOLDS,
        n_jobs=-1,
    )
    grid.fit(X_train, y_train)
    return grid


def _train_random_forest(X_train: pd.DataFrame, y_train: pd.Series) -> GridSearchCV:
    pipeline = Pipeline([
        ("preprocess", build_preprocessor()),
        ("model", RandomForestClassifier(class_weight="balanced", random_state=RANDOM_STATE)),
    ])
    grid = GridSearchCV(
        pipeline,
        param_grid={"model__n_estimators": [100, 300], "model__max_depth": [4, 8, None]},
        scoring="roc_auc",
        cv=CV_FOLDS,
        n_jobs=-1,
    )
    grid.fit(X_train, y_train)
    return grid


def _evaluate(name: str, grid: GridSearchCV, X_test: pd.DataFrame, y_test: pd.Series) -> ModelResult:
    best_pipeline = grid.best_estimator_
    predictions = best_pipeline.predict(X_test)
    probabilities = best_pipeline.predict_proba(X_test)[:, 1]

    preprocessor = best_pipeline.named_steps["preprocess"]
    feature_names = list(preprocessor.get_feature_names_out())
    model = best_pipeline.named_steps["model"]

    scores = model.feature_importances_ if hasattr(model, "feature_importances_") else model.coef_[0]
    ranked = sorted(zip(feature_names, scores), key=lambda pair: abs(pair[1]), reverse=True)[:10]
    interpretability = [{"feature": feature, "value": round(float(value), 4)} for feature, value in ranked]

    return ModelResult(
        name=name,
        best_params={key.replace("model__", ""): value for key, value in grid.best_params_.items()},
        cv_best_roc_auc=round(float(grid.best_score_), 4),
        test_roc_auc=round(float(roc_auc_score(y_test, probabilities)), 4),
        test_accuracy=round(float(best_pipeline.score(X_test, y_test)), 4),
        classification_report=classification_report(y_test, predictions, output_dict=True, zero_division=0),
        confusion_matrix=confusion_matrix(y_test, predictions).tolist(),
        interpretability=interpretability,
        pipeline=best_pipeline,
    )


def train_and_evaluate(df: pd.DataFrame) -> dict[str, ModelResult]:
    """Entrena y evalúa Logistic Regression y Random Forest sobre `conversion_flag`.

    Ambos modelos usan `class_weight="balanced"` para compensar el desbalance de
    clases (~11.5% de conversión en el dataset original) sin necesitar
    oversampling ni dependencias adicionales.
    """
    missing = set(FEATURE_COLUMNS + [TARGET_COLUMN]) - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas requeridas para el entrenamiento: {sorted(missing)}")

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y,
    )

    logistic_grid = _train_logistic(X_train, y_train)
    random_forest_grid = _train_random_forest(X_train, y_train)

    return {
        "logistic_regression": _evaluate("logistic_regression", logistic_grid, X_test, y_test),
        "random_forest": _evaluate("random_forest", random_forest_grid, X_test, y_test),
    }
