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
                    FastAPI propia
                         ↓
                Streamlit + Plotly
```

---

## Tres fuentes integradas

| Fuente                      | Tipo      | Uso                                            |
| --------------------------- | --------- | ---------------------------------------------- |
| `data/raw/bank.csv`         | CSV       | Información base de clientes y campañas.       |
| World Bank Indicators API   | REST JSON | Contexto macroeconómico de Portugal.           |
| `contact_channel_reference` | SQL local | Catálogo de canales para enriquecer registros. |

---

## Requisitos

* Python 3.12 recomendado.
* Conexión a internet para actualizar indicadores desde la API externa.
* Navegador web para visualizar FastAPI y Streamlit.
* Terminal de macOS.
* Homebrew recomendado para instalar Python 3.12 en computadores nuevos.

---

# Ejecución del proyecto desde cero

Esta sección explica cómo ejecutar el proyecto en un computador nuevo.

---

## 1. Entrar a la carpeta del proyecto

Abrir la terminal y entrar a la carpeta del proyecto:

```bash
cd ~/Downloads/bank-marketing-analytics
```

Verificar que se está dentro de la carpeta correcta:

```bash
ls
```

Deberían aparecer carpetas y archivos como:

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

---

## 2. Verificar versión de Python

Ejecutar:

```bash
python3 --version
```

Si aparece una versión antigua como:

```text
Python 3.9.6
```

se recomienda instalar Python 3.12.

Primero verificar si Python 3.12 ya existe:

```bash
python3.12 --version
```

Si aparece:

```text
Python 3.12.x
```

se puede continuar al paso 4.

---

## 3. Instalar Homebrew y Python 3.12

Si el comando `brew` no existe:

```bash
brew --version
```

y aparece:

```text
zsh: command not found: brew
```

instalar Homebrew con:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Al finalizar, Homebrew mostrará instrucciones similares a estas:

```bash
echo >> /Users/alumno14/.zprofile
echo 'eval "$(/opt/homebrew/bin/brew shellenv zsh)"' >> /Users/alumno14/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv zsh)"
```

Ejecutar esos comandos para agregar Homebrew al PATH.

Luego verificar:

```bash
brew --version
```

Instalar Python 3.12:

```bash
brew install python@3.12
```

Verificar instalación:

```bash
python3.12 --version
```

Resultado esperado:

```text
Python 3.12.x
```

---

## 4. Crear entorno virtual

Dentro de la carpeta raíz del proyecto, ejecutar:

```bash
python3.12 -m venv .venv
```

Activar el entorno virtual:

```bash
source .venv/bin/activate
```

Verificar que el entorno está usando Python 3.12:

```bash
python --version
```

Resultado esperado:

```text
Python 3.12.x
```

---

## 5. Instalar dependencias

Con el entorno virtual activado:

```bash
python -m pip install --upgrade pip
```

Luego instalar las librerías del proyecto:

```bash
pip install -r requirements.txt
```

---

## 6. Crear archivo de configuración

Crear el archivo `.env` desde el ejemplo incluido:

```bash
cp .env.example .env
```

Este archivo permite ejecutar el proyecto de forma local usando SQLite.

---

## 7. Ejecutar el pipeline ETL

Ejecutar:

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

Si aparece:

```text
cache_fallback
```

significa que la API externa no respondió y el sistema usó el respaldo local. Esto no impide ejecutar la demostración.

---

# Levantar la API

Abrir una nueva terminal.

Entrar nuevamente al proyecto:

```bash
cd ~/Downloads/bank-marketing-analytics
```

Activar el entorno virtual:

```bash
source .venv/bin/activate
```

Levantar FastAPI:

```bash
uvicorn api.main:app --reload
```

Resultado esperado:

```text
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

No cerrar esta terminal mientras se usa el dashboard.

Abrir en el navegador:

* API: `http://localhost:8000`
* Swagger: `http://localhost:8000/docs`
* Health check: `http://localhost:8000/health`

---

# Levantar el dashboard

Abrir otra terminal distinta.

Entrar al proyecto:

```bash
cd ~/Downloads/bank-marketing-analytics
```

Activar el entorno virtual:

```bash
source .venv/bin/activate
```

Ejecutar Streamlit agregando el proyecto al `PYTHONPATH`:

```bash
PYTHONPATH=. streamlit run dashboards/app.py
```

Abrir en el navegador:

```text
http://localhost:8501
```

---

# Terminales necesarias para la demo

Para demostrar el proyecto completo se deben mantener abiertas dos terminales al mismo tiempo.

## Terminal 1: API

```bash
cd ~/Downloads/bank-marketing-analytics
source .venv/bin/activate
uvicorn api.main:app --reload
```

Se visualiza en:

```text
http://localhost:8000/docs
```

## Terminal 2: Dashboard

```bash
cd ~/Downloads/bank-marketing-analytics
source .venv/bin/activate
PYTHONPATH=. streamlit run dashboards/app.py
```

Se visualiza en:

```text
http://localhost:8501
```

---

# Pruebas automatizadas

Para ejecutar las pruebas:

```bash
pytest
```

Resultado esperado:

```text
9 passed
```

También se puede ejecutar:

```bash
bash scripts/run_tests.sh
```

---

# Dashboard por audiencia

| Vista     | Usuario principal  | Contenido                                                     |
| --------- | ------------------ | ------------------------------------------------------------- |
| Ejecutiva | Gerencia           | KPIs, conversión, perfiles prioritarios y contexto económico. |
| Operativa | Equipo de campañas | Filtros, rendimiento por canal y descarga de muestras.        |
| Técnica   | Analistas          | Calidad de datos, ETL, PCA, K-Means y correlaciones.          |

---

# Robustez del pipeline

El pipeline incluye:

* Control de existencia y contenido del CSV.
* Validación de columnas obligatorias.
* Validación de dominios binarios.
* Conteo de duplicados, nulos y categorías `unknown`.
* Extracción desde API externa con reintentos limitados.
* Caché de contingencia para demo sin conexión.
* Fuente SQL local de referencia.
* Carga transaccional.
* Trazabilidad de ejecuciones.
* Logs rotativos.
* Tests automatizados.

---

# Evidencias recomendadas para la entrega

Se recomienda guardar capturas de pantalla de:

1. Ejecución exitosa del pipeline:

```text
Pipeline completado: 4521 filas cargadas
```

2. API funcionando en:

```text
http://localhost:8000/docs
```

3. Dashboard funcionando en:

```text
http://localhost:8501
```

4. Pruebas automatizadas aprobadas:

```text
9 passed
```

Estas evidencias pueden incluirse en la documentación o utilizarse durante la presentación.

---

# Errores frecuentes y soluciones

## Error: `python3.12: command not found`

Python 3.12 no está instalado. Instalarlo con Homebrew:

```bash
brew install python@3.12
```

Luego verificar:

```bash
python3.12 --version
```

---

## Error: `zsh: command not found: brew`

Homebrew no está instalado. Instalarlo con:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Luego ejecutar los comandos indicados por Homebrew en la sección `Next steps`.

---

## Error: `ModuleNotFoundError: No module named 'dashboards'`

Ejecutar Streamlit con `PYTHONPATH`:

```bash
PYTHONPATH=. streamlit run dashboards/app.py
```

---

## Error: `Connection refused` en el dashboard

Significa que FastAPI no está corriendo.

Primero levantar la API:

```bash
uvicorn api.main:app --reload
```

Después levantar Streamlit:

```bash
PYTHONPATH=. streamlit run dashboards/app.py
```

---

## Streamlit solicita un correo

Cuando aparezca:

```text
Email:
```

se puede dejar en blanco y presionar Enter.

---

# Documentación

* [Arquitectura](docs/arquitectura.md)
* [API](docs/api.md)
* [Manual de usuario](docs/manual_usuario.md)
* [Guía de instalación y ejecución local](docs/guia_despliegue.md)
* [Decisiones técnicas](docs/decisiones_tecnicas.md)
* [Trazabilidad contra la rúbrica](docs/rubrica_trazabilidad.md)
* [Estrategia Git](repo/estrategia_git.md)
* [Presentación](docs/presentacion.md)

---

# Nota sobre el caché de la API externa

`data/cache/world_bank_indicators_cache.json` incluye un respaldo para ejecutar la demo sin internet. Antes de la entrega final se recomienda ejecutar el ETL conectado a internet para que los valores sean refrescados directamente desde la API oficial.
