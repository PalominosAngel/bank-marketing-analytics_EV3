# Estrategia de colaboración en Git

## Ramas

```text
main
└── develop
    ├── feature/etl-pipeline
    ├── feature/database-local
    ├── feature/dashboard
    ├── feature/api
    ├── feature/testing
    └── docs/documentation
```

## Integrantes y responsabilidades iniciales

| Integrante | Responsabilidad principal |
|---|---|
| Benjamin Arratia | Pipeline ETL, validaciones y arquitectura |
| Angel Palominos | Base de datos local, scripts de ejecución y apoyo en pruebas |
| Maria Jose Alvarez | Dashboard, usabilidad y manual de usuario |

## Convención de commits

```text
feat(etl): agrega extracción desde API externa con caché
feat(dashboard): incorpora vista operativa con filtros
fix(api): controla respuesta cuando el ETL aún no fue ejecutado
test(validators): cubre error por columnas faltantes
docs(readme): documenta ejecución local reproducible
```

## Pull requests

Cada feature debe integrarse a `develop` mediante pull request. Otro integrante debe revisar el código antes del merge. La rama `main` se reserva para entregas estables.
