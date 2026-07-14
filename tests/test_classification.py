import pandas as pd

from models.classification import FEATURE_COLUMNS, TARGET_COLUMN, train_and_evaluate


def sample_frame(n: int = 60) -> pd.DataFrame:
    rows = []
    for i in range(n):
        rows.append({
            "age": 25 + (i % 40),
            "balance": 100 * (i % 10),
            "day": 1 + (i % 28),
            "campaign": 1 + (i % 5),
            "pdays": -1 if i % 2 else 30,
            "previous": i % 3,
            "job": "management" if i % 2 == 0 else "services",
            "marital": "single" if i % 2 == 0 else "married",
            "education": "tertiary",
            "default": "no",
            "housing": "yes" if i % 2 == 0 else "no",
            "loan": "no",
            "contact": "cellular",
            "month": "may",
            "poutcome": "unknown",
            TARGET_COLUMN: int(i % 3 == 0),
        })
    return pd.DataFrame(rows)


def test_train_and_evaluate_produces_metrics_for_both_models():
    results = train_and_evaluate(sample_frame())

    assert set(results) == {"logistic_regression", "random_forest"}
    for result in results.values():
        assert 0.0 <= result.test_roc_auc <= 1.0
        assert 0.0 <= result.test_accuracy <= 1.0
        # `previous` codifica casi exactamente el target sintético (ver sample_frame),
        # así que un modelo que de verdad aprende debe superar claramente el azar (0.5).
        assert result.test_roc_auc > 0.5, f"{result!r} no supera el azar — ¿pipeline roto o etiquetas mezcladas?"
        assert result.interpretability
        assert result.confusion_matrix
        assert result.best_params


def test_train_and_evaluate_fails_fast_on_missing_columns():
    frame = sample_frame().drop(columns=["age"])
    try:
        train_and_evaluate(frame)
        assert False, "Debió lanzar ValueError por columnas faltantes"
    except ValueError as exc:
        assert "age" in str(exc)


def test_feature_columns_exclude_duration_to_avoid_leakage():
    assert "duration" not in FEATURE_COLUMNS
    assert "duration_minutes" not in FEATURE_COLUMNS
