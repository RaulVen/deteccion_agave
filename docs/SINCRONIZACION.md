# Trabajar desde las dos computadoras

El repositorio compartido es <https://github.com/RaulVen/deteccion_agave> y la rama de trabajo acordada es `main`.

## Reparto del trabajo

| Trabajo | Lugar en el repositorio |
|---|---|
| Redactar capítulos y consultar sus PDF | [tesis/](tesis/README.md) |
| Artículo y bibliografía del artículo | [paper/](paper/) |
| Reportes Word anteriores | [reportes/](reportes/) |
| Consultar tablas, curvas y conteos sin GPU | [resultados/](resultados/README.md), [benchmark/](../benchmark/) |
| Preparar datos, entrenar y evaluar | [scripts/](../scripts/), [src/](../src/), [configs/](../configs/) |
| Cámara y Raspberry Pi | [hardware/](../hardware/README.md) |

La computadora de redacción solo necesita Git y el editor de documentos que utilices. No necesita instalar CUDA, PyTorch ni el entorno de entrenamiento para leer o editar Markdown, LaTeX, Word o PDF. Compilar un documento requiere las herramientas indicadas por su generador.

## Primera vez en la otra computadora

Si todavía no tienes una copia del repositorio:

```powershell
git clone https://github.com/RaulVen/deteccion_agave.git
cd deteccion_agave
git switch main
```

Abre esa carpeta como proyecto. Si ya existe una copia con trabajo tuyo, úsala y revisa su estado antes de descargar; no clones encima ni reemplaces sus archivos.

## Antes de empezar cada sesión

Desde la carpeta del repositorio:

```powershell
git status
git branch --show-current
git pull --ff-only origin main
```

El flujo supone estar en `main`. Si `git status` muestra trabajo sin guardar en Git, consérvalo primero y revisa antes de cambiar de rama o integrar cambios. Si `pull --ff-only` informa divergencia, detente y pide integrar ambos historiales conservando sus cambios.

## Al terminar de redactar

Revisa y sube únicamente lo que cambiaste. Por ejemplo, si trabajaste en los capítulos:

```powershell
git diff -- docs/tesis
git add docs/tesis
git diff --cached --stat
git commit -m "Actualiza redaccion de tesis"
git push origin main
```

Agrega también `docs/paper` o `docs/reportes` si los modificaste. Los PDF y Word no se fusionan como texto: evita editar el mismo archivo en ambas computadoras a la vez. Al cambiar de equipo, termina el push en uno y haz pull en el otro.

## Al terminar el trabajo computacional

Revisa código, configuraciones y resultados, y agrega los archivos correspondientes antes de hacer commit y push. Cuando haya resultados nuevos útiles para el escrito, publica las tablas, curvas y una nota de procedencia en `docs/resultados/`; conserva las limitaciones del experimento. No hace falta volver a entrenar para sincronizar.

Los archivos `status.json`, `launch.json`, metadatos y registros de épocas que acompañan las campañas son evidencia histórica. Que se descarguen en otra PC no significa que haya un entrenamiento activo allí. No lances las campañas desde la computadora de redacción.

## Archivos que siguen siendo locales

`.gitignore` excluye `.venv`, imágenes/etiquetas de datasets, ZIP, videos, corridas completas, pesos, binarios de modelo, instalaciones de terceros, credenciales, cachés, logs y respaldos. No se borran de la computadora de cómputo y no llegan mediante pull. Los manifiestos, configuraciones, resúmenes y evidencia seleccionada sí se versionan.

Git no replica automáticamente el historial de chats. Para continuar la redacción en otro chat, usa el índice de `docs/tesis/` y el documento de contexto allí incluido. Trabaja sobre los archivos del repositorio; las copias originales en la carpeta local `Documents/ChatGPT/tesis` se conservaron como respaldo de esta integración y no se actualizan automáticamente.

Las rutas absolutas que aparezcan en CSV/JSON históricos son datos de procedencia. Los accesos principales de la documentación usan rutas relativas para funcionar en ambas computadoras.

## Si el push es rechazado

Otra computadora pudo subir cambios antes. No uses `--force`. Descarga y revisa los cambios remotos, integra las dos versiones y vuelve a subir. En este chat puedes pedir «sincroniza con main conservando los cambios de ambas computadoras».
