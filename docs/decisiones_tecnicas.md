# Decisiones técnicas y alcance

## Segmentación de clientes

Se aplican `StandardScaler`, PCA y K-Means sobre edad, saldo, duración, cantidad de intentos, días desde contacto anterior y contactos previos. Se utilizan cuatro clusters con semilla fija para mantener reproducibilidad.

## Tratamiento de categorías `unknown`

No se eliminan automáticamente. Se conservan porque representan información ausente o no registrada y forman parte de la realidad del dataset. El dashboard técnico cuantifica estas categorías para transparentar la calidad de los datos.

## Capado de outliers (balance y duration)

Segunda técnica de limpieza, complementaria a la anterior: a diferencia de las categorías `unknown` (que se conservan tal cual), los valores numéricos extremos de `balance` y `duration` sí se ajustan, porque distorsionan por igual el escalamiento de K-Means/PCA y de los modelos supervisados sin aportar señal adicional más allá de "es un extremo".

- Método: capado (winsorización) vía rango intercuartílico, límite = `Q1 - 1.5·IQR` a `Q3 + 1.5·IQR`, aplicado en `etl/transform.py::cap_outliers_iqr`.
- Impacto cuantificado sobre `data/raw/bank.csv`: ~506 registros de `balance` (11.2%) y ~330 registros de `duration` (7.3%) quedan fuera del rango y se capan a sus límites. El conteo exacto de cada ejecución queda registrado en `data_quality_report` (columnas `balance_outliers_capped` y `duration_outliers_capped`), visible en el dashboard técnico.
- Se eligió capar en vez de eliminar para no perder ~11-18% del dataset original (solo 4521 filas), a costa de introducir un sesgo leve hacia los límites del IQR en esas colas.

## Clasificación supervisada: predicción de conversión (`models/`)

La segmentación K-Means/PCA es exploratoria y no reemplaza un modelo predictivo (ver "Limitaciones" más abajo); `models/classification.py` cierra ese vacío con clasificación binaria supervisada sobre `conversion_flag` (¿el cliente contrata el depósito a plazo?).

- **Algoritmos**: `LogisticRegression` (baseline interpretable, coeficientes explicables a negocio) y `RandomForestClassifier` (captura interacciones no lineales entre variables). Ambos con `class_weight="balanced"` para compensar el desbalance de clases (~11.5% de conversión en el dataset original), sin necesidad de oversampling ni dependencias adicionales.
- **Tuning**: `GridSearchCV` (cv=3, scoring `roc_auc`) sobre `C` en la regresión logística y sobre `n_estimators`/`max_depth` en el Random Forest.
- **Exclusión deliberada de `duration`**: la duración de la llamada es un caso clásico de fuga de información (*data leakage*) documentado en el propio dataset UCI Bank Marketing — solo se conoce después de realizar la llamada (si dura 0, `y` es necesariamente "no"), por lo que un modelo que la use no sirve para decidir a quién llamar de antemano. Se excluye tanto `duration` como `duration_minutes` del set de features.
- **Selección del mejor modelo**: `models/train.py` compara ambos algoritmos por `roc_auc` en test (métrica agregada e independiente del umbral, apta para comparar modelos). El costo de no identificar a un cliente que sí convertiría (no contactarlo) es más alto que el de contactar a alguien que no convierte, por lo que además de `roc_auc` se reporta el `classification_report` completo (con `recall`/`precision` por clase) en `models/metrics.json`: ese detalle es el que debe guiar, en un paso posterior, la elección del umbral de decisión operativo (a qué clientes contactar), no la elección entre modelos. `class_weight="balanced"` compensa el desbalance de clases durante el entrenamiento de ambos algoritmos.
- **Resultado de referencia**: ~0.72-0.73 de ROC AUC en test para ambos modelos sobre el dataset completo — razonable para un modelo pre-llamada sin `duration`, consistente con lo reportado en la literatura sobre este dataset.
- **Interpretabilidad**: coeficientes (regresión logística) y `feature_importances_` (Random Forest) de las 10 variables más influyentes, expuestos en `models/metrics.json` y en el dashboard técnico.

## Limitaciones

- El archivo original no contiene una fecha completa de campaña ni un identificador natural del cliente.
- Los indicadores macroeconómicos contextualizan el análisis, pero no permiten inferir causalidad individual.
- La segmentación K-Means/PCA es descriptiva; la predicción de conversión la cubre `models/classification.py` (ver sección anterior), pero ambas siguen sin reemplazar una evaluación comercial completa.
- El caché incluido permite una demo offline. Antes de la entrega final debe ejecutarse el pipeline conectado a internet para refrescar los datos oficiales.
- No se usa Docker/CI-CD: decisión documentada en `docs/alcance_sin_docker.md`, priorizando una ejecución local simple y defendible sobre el cumplimiento literal de esa parte del enunciado del Encargo.
