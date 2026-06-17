# Decisiones técnicas y alcance

## Segmentación de clientes

Se aplican `StandardScaler`, PCA y K-Means sobre edad, saldo, duración, cantidad de intentos, días desde contacto anterior y contactos previos. Se utilizan cuatro clusters con semilla fija para mantener reproducibilidad.

## Tratamiento de categorías `unknown`

No se eliminan automáticamente. Se conservan porque representan información ausente o no registrada y forman parte de la realidad del dataset. El dashboard técnico cuantifica estas categorías para transparentar la calidad de los datos.

## Limitaciones

- El archivo original no contiene una fecha completa de campaña ni un identificador natural del cliente.
- Los indicadores macroeconómicos contextualizan el análisis, pero no permiten inferir causalidad individual.
- La segmentación es descriptiva; no reemplaza un modelo predictivo supervisado ni una evaluación comercial.
- El caché incluido permite una demo offline. Antes de la entrega final debe ejecutarse el pipeline conectado a internet para refrescar los datos oficiales.
