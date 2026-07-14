# Bank Marketing Analytics

Plataforma analítica end-to-end para estudiar campañas bancarias, segmentar clientes y entregar visualizaciones diferenciadas para audiencias ejecutivas, operativas y técnicas.

## Integrantes

* Angel Palominos
* Benjamin Arratia
* Maria Jose Alvarez

## Objetivo académico

El proyecto fue construido para demostrar integración de fuentes, pipeline ETL, validación de datos, manejo de errores, visualización interactiva, testing automatizado y colaboración mediante Git.

> **Nota de alcance:** esta versión se ejecuta de forma local con entorno virtual de Python. No utiliza Docker, porque el equipo priorizó una ejecución simple, reproducible y fácil de defender durante la evaluación.

---

## Tabla de contenidos

1. [Arquitectura resumida](#arquitectura-resumida)
2. [Estructura del proyecto](#estructura-del-proyecto)
3. [Tres fuentes integradas](#tres-fuentes-integradas)
4. [Requisitos](#requisitos)
5. [Instalación y ejecución](#instalación-y-ejecución)
   * [Opción rápida con Makefile (macOS/Linux)](#opción-rápida-con-makefile-macoslinux)
   * [Instalación manual paso a paso](#instalación-manual-paso-a-paso)
6. [Terminales necesarias para la demo](#terminales-necesarias-para-la-demo)
7. [Pruebas automatizadas](#pruebas-automatizadas)
8. [Dashboard por audiencia](#dashboard-por-audiencia)
9. [Robustez del pipeline](#robustez-del-pipeline)
10. [Evidencias recomendadas para la entrega](#evidencias-recomendadas-para-la-entrega)
11. [Errores frecuentes y soluciones](#errores-frecuentes-y-soluciones)
12. [Documentación](#documentación)
13. [Nota sobre el caché de la API externa](#nota-sobre-el-caché-de-la-api-externa)

---

## Arquitectura resumida

```text
bank.csv + World Bank REST API + catálogo SQL de canales
                         ↓
           Pipeline ETL con validaciones y logs
                         ↓
              PCA + K-Means exploratorio
                         ↓
                    SQLite local
                         ↓
      Clasificación supervisada (Logistic Regression + Random Forest)
                         ↓
                    FastAPI propia
                         ↓
                Streamlit + Plotly
```

---

## Estructura del proyecto

```text
bank-marketing-analytics/
├── api/                  # FastAPI: endpoints que exponen los datos procesados
├── dashboards/            # Streamlit + Plotly
│   └── pages/             # Vistas: ejecutiva, operativa y técnica
├── data/
│   ├── raw/               # bank.csv (fuente original, no se modifica)
│   └── cache/             # Respaldo local de la World Bank API para demo offline
├── database/              # init.sql y seed.sql del catálogo de canales
├── docs/                  # Documentación del proyecto
│   ├── colaboracion/      # Estrategia Git, issues planificados y checklist de evidencias
│   ├── diagramas/         # Diagrama Mermaid de arquitectura
│   └── img/               # Capturas usadas en la presentación
├── etl/                   # Pipeline: extract, transform, clustering, load, validators
│   └── notebooks/         # Exploración inicial en Jupyter
├── models/                 # Clasificación supervisada: entrenamiento, métricas y modelos serializados
│   └── artifacts/          # Modelos entrenados (.joblib) — regenerable, no se versiona
├── scripts/                # run_local.sh y run_tests.sh
├── tests/                  # Pruebas automatizadas (pytest)
├── .env.example            # Plantilla de configuración
├── Makefile                # Atajos: install, etl, train-models, api, dashboard, test, clean
├── requirements.txt
└── README.md
```

> Las carpetas `data/database/` (SQLite) y `logs/` se generan automáticamente al ejecutar el pipeline; no forman parte del repositorio (ver `.gitignore`).

---

## Tres fuentes integradas

| Fuente                      | Tipo      | Uso                                            |
| --------------------------- | --------- | ---------------------------------------------- |
| `data/raw/bank.csv`         | CSV       | Información base de clientes y campañas.       |
| World Bank Indicators API   | REST JSON | Contexto macroeconómico de Portugal.           |
| `contact_channel_reference` | SQL local | Catálogo de canales para enriquecer registros. |

---

## Requisitos

* **Python 3.12** (recomendado; evitar 3.13/3.14 — ver nota más abajo).
* Conexión a internet para actualizar indicadores desde la API externa.
* Navegador web para visualizar FastAPI y Streamlit.
* Terminal de macOS, PowerShell o CMD en Windows.
* Homebrew recomendado en macOS para instalar Python 3.12 si no está disponible.
* En Windows se recomienda instalar Python 3.12 desde el sitio oficial de Python y marcar la opción **Add Python to PATH** durante la instalación.

> **Por qué Python 3.12 y no una versión más nueva:** Homebrew retira versiones antiguas de Python de sus fórmulas con cada actualización mayor. Si el entorno virtual se crea apuntando a un intérprete que Homebrew luego elimina (por ejemplo, `python@3.13` cuando Homebrew ya solo ofrece `3.14`), el `.venv` queda inutilizable y hay que recrearlo desde cero. Fijar `3.12` explícitamente evita ese problema.

---

## Instalación y ejecución

> **Importante:** en los comandos donde aparezca `RUTA_DEL_PROYECTO`, reemplazar por la ubicación real donde se descomprimió o clonó el proyecto (por ejemplo, `Downloads`, `Desktop` o `Documentos`).

### Opción rápida con Makefile (macOS/Linux)

Si el sistema tiene `make` instalado (viene por defecto en macOS y en la mayoría de distribuciones Linux), esta es la vía más corta:

```bash
make install       # crea .venv e instala dependencias
cp .env.example .env
make etl           # ejecuta el pipeline ETL
make train-models  # entrena los modelos de clasificación supervisada
```

Luego, en dos terminales distintas (dentro de la misma carpeta del proyecto, con `.venv` activado no es necesario porque `make` ya usa el intérprete del venv vía el target `install`):

```bash
make api        # Terminal 1 — FastAPI en http://localhost:8000
make dashboard  # Terminal 2 — Streamlit en http://localhost:8501
```

Y para las pruebas automatizadas:

```bash
make test
```

Windows no trae `make` por defecto (requiere instalarlo aparte, por ejemplo con `choco install make`). Si no se cuenta con `make`, seguir la instalación manual a continuación.

### Instalación manual paso a paso

#### 1. Entrar a la carpeta del proyecto

**macOS**

Abrir la terminal y entrar a la carpeta donde está el proyecto.

```bash
cd ~/Downloads/bank-marketing-analytics
```

También se puede escribir `cd`, dejar un espacio, arrastrar la carpeta del proyecto a la terminal y presionar Enter.

Verificar que se está dentro de la carpeta correcta:

```bash
ls
```

**Windows (PowerShell o CMD)**

```powershell
cd "$env:USERPROFILE\Downloads\bank-marketing-analytics"
```

Verificar que se está dentro de la carpeta correcta:

```powershell
dir
```

En ambos casos deberían aparecer carpetas y archivos como:

```text
api
dashboards
data
docs
etl
requirements.txt
README.md
tests
```

#### 2. Verificar versión de Python

**macOS**

```bash
python3 --version
```

Si aparece una versión antigua (por ejemplo `Python 3.9.6`), se recomienda instalar Python 3.12. Primero verificar si ya existe:

```bash
python3.12 --version
```

Si aparece `Python 3.12.x`, se puede continuar con la creación del entorno virtual.

**Windows**

```powershell
python --version
```

o:

```powershell
py --version
```

Resultado esperado: `Python 3.12.x`.

Si Python no está instalado o aparece una versión antigua, instalar Python 3.12 desde el sitio oficial de Python marcando **Add Python to PATH** durante la instalación, y luego cerrar y volver a abrir PowerShell.

#### 3. Instalar Python 3.12 en macOS (si es necesario)

Si el comando `brew` no existe:

```bash
brew --version
```

y aparece `zsh: command not found: brew`, instalar Homebrew con:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Al finalizar, Homebrew mostrará instrucciones similares a estas — ejecutarlas para agregarlo al PATH:

```bash
echo >> /Users/USUARIO/.zprofile
echo 'eval "$(/opt/homebrew/bin/brew shellenv zsh)"' >> /Users/USUARIO/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv zsh)"
```

Luego verificar e instalar Python 3.12:

```bash
brew --version
brew install python@3.12
python3.12 --version
```

Resultado esperado: `Python 3.12.x`.

#### 4. Crear entorno virtual

**macOS**

```bash
python3.12 -m venv .venv
```

Si `python3.12` no existe pero `python3` ya corresponde a Python 3.12, usar `python3 -m venv .venv`.

Activar y verificar:

```bash
source .venv/bin/activate
python --version
```

**Windows PowerShell**

```powershell
python -m venv .venv
```

o `py -3.12 -m venv .venv`.

Activar el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación, ejecutar y volver a activar:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
```

**Windows CMD**

```cmd
python -m venv .venv
.venv\Scripts\activate
```

En los tres casos, verificar versión con `python --version` → `Python 3.12.x`.

#### 5. Instalar dependencias

Con el entorno virtual activado (macOS y Windows):

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### 6. Crear archivo de configuración

Crear el archivo `.env` desde el ejemplo incluido. Este archivo permite ejecutar el proyecto de forma local usando SQLite.

| Sistema         | Comando                     |
| --------------- | ---------------------------- |
| macOS           | `cp .env.example .env`       |
| Windows PowerShell | `Copy-Item .env.example .env` |
| Windows CMD     | `copy .env.example .env`     |

#### 7. Ejecutar el pipeline ETL

```bash
python -m etl.pipeline
```

Resultado esperado:

```text
Fuente CSV extraída: 4521 filas
Fuente SQL extraída: 3 canales de contacto
Fuente API externa extraída con estado: live_api
Pipeline completado: 4521 filas cargadas
```

Si aparece `cache_fallback`, significa que la API externa no respondió y el sistema usó el respaldo local. Esto no impide ejecutar la demostración.

#### 8. Entrenar los modelos de clasificación supervisada

Requiere haber corrido el pipeline ETL primero (paso 7), ya que lee `data/processed/customers_processed.csv`.

```bash
python -m models.train
```

Resultado esperado:

```text
Entrenamiento completado. Mejor modelo: logistic_regression (ROC AUC test: 0.73)
```

Esto genera `models/metrics.json` (comparación de modelos, métricas e interpretabilidad — se versiona) y `models/artifacts/*.joblib` (modelos serializados — regenerable, no se versiona). Ver `docs/decisiones_tecnicas.md` para la justificación de algoritmos y por qué se excluye `duration` de las features.

### Levantar la API

Abrir una nueva terminal, entrar nuevamente a la carpeta del proyecto y activar el entorno virtual.

**macOS**

```bash
cd RUTA_DEL_PROYECTO
source .venv/bin/activate
uvicorn api.main:app --reload
```

**Windows PowerShell**

```powershell
cd RUTA_DEL_PROYECTO
.\.venv\Scripts\Activate.ps1
uvicorn api.main:app --reload
```

Resultado esperado:

```text
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

No cerrar esta terminal mientras se usa el dashboard. Abrir en el navegador:

* API: `http://localhost:8000`
* Swagger: `http://localhost:8000/docs`
* Health check: `http://localhost:8000/health`

### Levantar el dashboard

Abrir **otra** terminal distinta, entrar nuevamente a la carpeta del proyecto y activar el entorno virtual. El dashboard necesita el proyecto en el `PYTHONPATH` para poder importar el paquete `dashboards`.

**macOS**

```bash
cd RUTA_DEL_PROYECTO
source .venv/bin/activate
PYTHONPATH=. streamlit run dashboards/app.py
```

**Windows PowerShell**

```powershell
cd RUTA_DEL_PROYECTO
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH="."
streamlit run dashboards/app.py
```

**Windows CMD**

```cmd
cd RUTA_DEL_PROYECTO
.venv\Scripts\activate
set PYTHONPATH=.
streamlit run dashboards/app.py
```

Abrir en el navegador: `http://localhost:8501`

Si Streamlit solicita un correo (`Email:`), se puede dejar en blanco y presionar Enter.

---

## Terminales necesarias para la demo

Para demostrar el proyecto completo se deben mantener abiertas **dos terminales** al mismo tiempo (además de la que ejecutó el pipeline ETL, que ya puede cerrarse):

| Terminal | Comando | URL |
| --- | --- | --- |
| 1 — API | `uvicorn api.main:app --reload` (ver [Levantar la API](#levantar-la-api)) | `http://localhost:8000/docs` |
| 2 — Dashboard | `PYTHONPATH=. streamlit run dashboards/app.py` (ver [Levantar el dashboard](#levantar-el-dashboard)) | `http://localhost:8501` |

---

## Pruebas automatizadas

```bash
pytest
```

Resultado esperado:

```text
21 passed
```

También se puede ejecutar:

| Sistema | Comando |
| --- | --- |
| macOS | `bash scripts/run_tests.sh` |
| Windows | `pytest` |

---

## Dashboard por audiencia

| Vista     | Usuario principal  | Contenido                                                     |
| --------- | ------------------ | --------------------------------------------------------------- |
| Ejecutiva | Gerencia           | KPIs, conversión, perfiles prioritarios y contexto económico.   |
| Operativa | Equipo de campañas | Filtros, rendimiento por canal, perfil por ocupación/estado civil y descarga de muestras. |
| Técnica   | Analistas          | Calidad de datos, ETL, PCA, K-Means, correlaciones y comparación de modelos de clasificación supervisada. |

---

## Robustez del pipeline

El pipeline incluye:

* Control de existencia y contenido del CSV.
* Validación de columnas obligatorias.
* Validación de dominios binarios.
* Conteo de duplicados, nulos y categorías `unknown`.
* Capado de outliers (IQR) en `balance` y `duration`, cuantificado en el reporte de calidad.
* Lectura por chunks para archivos grandes (`etl/extract.py`).
* Extracción desde API externa con reintentos limitados.
* Caché de contingencia para demo sin conexión.
* Fuente SQL local de referencia.
* Carga transaccional.
* Trazabilidad de ejecuciones.
* Logs rotativos.
* Tests automatizados.

---

## Evidencias recomendadas para la entrega

Se recomienda guardar capturas de pantalla de:

1. Ejecución exitosa del pipeline: `Pipeline completado: 4521 filas cargadas`
2. Entrenamiento de modelos: `Entrenamiento completado. Mejor modelo: ...`
3. API funcionando en: `http://localhost:8000/docs`
4. Dashboard funcionando en: `http://localhost:8501`
5. Pruebas automatizadas aprobadas: `21 passed`

Estas evidencias pueden utilizarse durante la presentación.

---

## Errores frecuentes y soluciones

### Error: `python3.12: command not found`

Python 3.12 no está instalado.

* **macOS:** `brew install python@3.12 && python3.12 --version`
* **Windows:** instalar Python 3.12 desde el sitio oficial marcando **Add Python to PATH**, luego cerrar y abrir nuevamente PowerShell.

### Error: `zsh: command not found: brew`

Homebrew no está instalado. Instalarlo con:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Luego ejecutar los comandos indicados por Homebrew en la sección `Next steps`.

### Error en Windows: `running scripts is disabled on this system`

PowerShell bloqueó la activación del entorno virtual:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
```

### Error: `ModuleNotFoundError: No module named 'dashboards'`

Ejecutar Streamlit agregando el proyecto al `PYTHONPATH` (ver [Levantar el dashboard](#levantar-el-dashboard)):

| Sistema | Comando |
| --- | --- |
| macOS | `PYTHONPATH=. streamlit run dashboards/app.py` |
| Windows PowerShell | `$env:PYTHONPATH="."` seguido de `streamlit run dashboards/app.py` |
| Windows CMD | `set PYTHONPATH=.` seguido de `streamlit run dashboards/app.py` |

### Error: `Connection refused` en el dashboard

Significa que FastAPI no está corriendo. Levantar primero la API (`uvicorn api.main:app --reload`) y después el dashboard.

---

## Documentación

* [Arquitectura](docs/arquitectura.md)
* [API](docs/api.md)
* [Manual de usuario](docs/manual_usuario.md)
* [Decisiones técnicas](docs/decisiones_tecnicas.md)
* [Alcance sin Docker](docs/alcance_sin_docker.md)
* [Trazabilidad contra la rúbrica](docs/rubrica_trazabilidad.md)
* [Presentación](docs/presentacion.md)
* [Estrategia Git](docs/colaboracion/estrategia_git.md)
* [Issues planificados](docs/colaboracion/issues_planificados.md)
* [Checklist de evidencias](docs/colaboracion/checklist_evidencias.md)

---

## Nota sobre el caché de la API externa

`data/cache/world_bank_indicators_cache.json` incluye un respaldo para ejecutar la demo sin internet. Antes de la entrega final se recomienda ejecutar el ETL conectado a internet para que los valores sean refrescados directamente desde la API oficial.
