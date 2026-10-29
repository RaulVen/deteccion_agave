# Deteccion de agave

Proyecto de deteccion, seguimiento y conteo de agaves con YOLO26. Reorganizado el 21 de octubre de 2026 para entrenar con las imagenes originales y las nuevas escenas con maleza.

## Trabajo entre computadoras

Este repositorio reúne la redacción y el trabajo computacional. La rama compartida es **`main`**. Antes de trabajar descarga los cambios; al terminar guarda un commit y haz push. Consulta la [guía de sincronización](docs/SINCRONIZACION.md) para la primera descarga y para conservar los cambios de ambos equipos.

| Necesito… | Abrir |
|---|---|
| Continuar la tesis en la computadora de redacción | [Índice de capítulos y contexto](docs/tesis/README.md) |
| Consultar resultados y figuras sin entrenar | [Evidencia para redacción](docs/resultados/README.md) |
| Editar el artículo o revisar reportes anteriores | [Artículo](docs/paper/), [reportes Word](docs/reportes/) |
| Trabajar en detección, seguimiento o entrenamiento | [scripts](scripts/), [src](src/), [configs](configs/), [benchmark](benchmark/) |
| Trabajar con la cámara y Raspberry Pi | [Prototipo y requisitos](hardware/README.md) |

Los capítulos y la evidencia se pueden consultar sin instalar el entorno de entrenamiento. Los datasets completos, pesos, videos, entornos y credenciales permanecen en la computadora de cómputo; Git comparte el código, documentos y resultados seleccionados.

## Dataset listo para la nueva etapa

Entrada: `datasets/prepared/agave_maleza_2026-10-21/data.yaml`.

| Procedencia | Entrenamiento | Validacion | Prueba | Reserva | Total |
|---|---:|---:|---:|---:|---:|
| Dataset anterior | 295 | 73 | 36 | 0 | 404 |
| Nuevas imagenes con maleza | 1198 | 362 | 100 | 166 | 1826 |
| **Combinado** | **1493** | **435** | **136** | **166** | **2230** |

Hay 2064 imagenes activas y 166 conservadas en reserva. Todas mantienen la resolucion original de 2880x1620 y la clase unica `agave`; la maleza es contexto/fondo, no una clase nueva. El redimensionado a 640 o 960, segun el experimento, y los aumentos se aplican durante el entrenamiento.

Los clips nuevos se agrupan por tramos; se reservan 60 segundos a cada lado de las fronteras entre particiones para reducir la similitud temporal. `images/reserve` y `labels/reserve` guardan esos fotogramas y no aparecen en `data.yaml`. La evaluacion sigue siendo interna a una misma salida de campo: no demuestra generalizacion a otro terreno o fecha. La particion historica se mantiene intacta.

Consultar [la preparacion y sus verificaciones](docs/REORGANIZACION_Y_DATASET.md), el `manifest.csv`, `summary.json` y `split_policy.json` dentro del dataset.

La comprobacion final de lectura con Ultralytics y ejecucion en GPU paso. Antes de entrenar conviene revisar [dos casos de anotacion](docs/dataset_2026-10-21/REVISION_ETIQUETAS.md) detectados en una muestra visual: posibles plantas sin caja y un fragmento de hoja en una imagen negativa.

## Ultima campaña completada: opciones 3 y 4, 150 epocas completas

Autorizada el 22 de octubre de 2026: **YOLO26s + SGD a 960** y despues **YOLO26s + SGD a 640 con `box=9.0`**, ambos con 150 epocas, `patience=0`, `time=null`, inversion vertical desactivada y los mismos aumentos de iluminacion. Cada experimento cambia un hiperparametro respecto a la referencia SGD de la primera campaña.

Ambos completaron las 150 epocas y las evaluaciones el 22 de octubre de 2026. [Comparacion de los cuatro modelos y graficas](docs/COMPARACION_CUATRO_MODELOS_150_EPOCAS_2026-10-22.md).

- [Protocolo de las opciones 3 y 4](docs/ENTRENAMIENTO_OPCIONES_3_4_150_EPOCAS.md).
- Configuraciones: `configs/training/agave_maleza_150ep_opciones34_2026-10-22/`.
- Corridas: `runs/detect/agave_maleza_150ep_opciones34_2026-10-22/`.
- Estado y resultados: `benchmark/agave_maleza_150ep_opciones34_2026-10-22/`.
- Comprobacion: `.\.venv\Scripts\python.exe -B scripts\train_campaign_opciones34_150.py --check`.
- Lanzamiento unico: `scripts/start_campaign_opciones34_150.ps1`.
- Seguimiento durante la ejecucion cada 30 minutos; se pausa al entregar el informe final.

El benchmark principal se evalua a 640 para compararlo con las dos corridas completadas. La evaluacion adicional a 960 del nuevo modelo y de la referencia se guarda separada.

## Primera campaña completada: dos modelos, 150 epocas completas

Se seleccionaron **YOLO26s con SGD** y **YOLO26n con aumentos de campo**, ambos a 640, con **150 epocas, sin parada temprana** (`patience=0`, `time=null`). Se elimino la inversion vertical (`flipud=0`) y se conservaron los aumentos HSV de brillo, saturacion y tono, junto con el resto del protocolo.

Ambos terminaron las 150 epocas. [Resultados y graficas](docs/RESULTADOS_150_EPOCAS_2026-10-22.md) y [protocolo](docs/ENTRENAMIENTO_150_EPOCAS.md).

- Configuraciones: `configs/training/agave_maleza_150ep_2026-10-21/`.
- Corridas: `runs/detect/agave_maleza_150ep_2026-10-21/`.
- Estado, logs y resultados: `benchmark/agave_maleza_150ep_2026-10-21/`.
- Cada corrida conserva `results.csv`, graficas `results.png`, `best.pt`, `last.pt` y checkpoints cada 10 epocas.

Para comprobar la configuracion antes del primer lanzamiento:

```powershell
.\.venv\Scripts\python.exe scripts\train_campaign_150.py --check
```

El lanzamiento se realiza una sola vez con `scripts/start_campaign_150.ps1`. Cuando exista `launch.json`, consultar el estado antes de volver a ejecutar: el lanzador evita duplicar esta campaña. Los resultados anteriores se conservan intactos.

Las once configuraciones de la propuesta anterior siguen archivadas en `configs/training/agave_maleza_2026-10-21/` y documentadas en [el protocolo anterior](docs/PROTOCOLO_REENTRENAMIENTO.md).

Los CSV historicos usan otro test. Para comparar pesos antiguos y nuevos se necesita evaluarlos sobre el mismo conjunto con los mismos parametros; no interpretar diferencias entre CSV distintos como una mejora controlada.

## Donde esta cada cosa

| Carpeta | Contenido |
|---|---|
| `datasets/prepared/agave_maleza_2026-10-21/` | Imagenes y etiquetas combinadas; entrada para entrenar |
| `datasets/raw/maleza_2026-10-21/` | ZIP nuevo original, metadatos y SHA-256 |
| `datasets/yolo26/` | Dataset historico de 404 imagenes, intacto |
| `datasets/agave.yolo26.zip` | Exportacion original anterior |
| `configs/training/agave_maleza_150ep_opciones34_2026-10-22/` | Opciones 3 y 4: resolucion 960 y peso de cajas 9.0 |
| `configs/training/agave_maleza_150ep_2026-10-21/` | Dos configuraciones completadas de 150 epocas |
| `configs/training/agave_maleza_2026-10-21/` | Propuesta anterior de 11 configuraciones |
| `configs/training/historico_2026-05_06/` | 10 configuraciones originales, conservadas sin cambios |
| `configs/datasets/` | Regla reproducible de particion |
| `configs/tracking/` | BoT-SORT para seguimiento y conteo |
| `models/pretrained/` | Pesos base YOLO26n y YOLO26s |
| `runs/` | Corridas y checkpoints; los historicos conservan sus rutas |
| `benchmark/` | CSV historico y nueva serie por separado |
| `docs/reportes/` | Reportes Word anteriores |
| `docs/paper/` | Articulo, PDF, fuentes y referencias |
| `docs/evidencia/` | Analisis, estadisticas y figuras del dataset anterior |
| `docs/results/` | Figuras de reportes anteriores |
| `scripts/` | Preparacion de datos, entrenamiento, reportes y conteo |
| `src/` | Analisis reproducibles del estudio historico |
| `video_predictions/` | Videos y conteos historicos |
| `backups/reorganizacion_2026-10-21/` | Copia previa de documentos/codigo y registro verificado de movimientos |

Los scripts de reportes y `src/` siguen analizando el estudio historico; no deben usarse para presentar resultados del dataset nuevo hasta tener corridas y actualizar el analisis.

El [archivo historico](docs/HISTORICO_BENCHMARK.md) conserva el benchmark completo, las instrucciones de tracking, los avances del articulo y las metricas previas. El mejor modelo anterior permanece en `runs/detect/agave_experiments/yolo26s_sgd_cos_slow_120e/weights/best.pt`.

## Entorno y archivos locales

Python 3.12; versiones del entrenamiento fijadas en `Pipfile.lock`: Ultralytics 8.4.57, PyTorch 2.10.0+cu128 y torchvision 0.25.0+cu128. No se reinstalo el entorno. Se conservan Git, los cambios locales anteriores y los resultados existentes.

Imagenes, etiquetas, ZIP, pesos, videos, corridas y respaldos quedan fuera de Git mediante `.gitignore`. Las tablas y figuras seleccionadas se conservan en `docs/resultados/` para su consulta desde la computadora de redacción.
