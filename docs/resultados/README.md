# Resultados para consulta y redacción

Copia de evidencia ligera preparada el 28 de octubre de 2026 para trabajar desde otra computadora sin instalar el entorno de entrenamiento ni descargar pesos, datasets o videos. Los archivos son copias exactas de resultados existentes: no se repitieron experimentos ni se cambiaron cifras. Las fechas de los experimentos siguen siendo las de las fuentes.

## Mapa de fuentes y copias

Las rutas de esta tabla parten de la raíz del repositorio. Dentro de cada copia se conserva la estructura relativa de su fuente.

| Fuente en la computadora de cálculo | Copia versionada |
|---|---|
| `runs/detect/agave_maleza_150ep_2026-10-21/yolo26s_sgd_640_150e/` | `docs/resultados/agave_maleza_150ep_2026-10-21/yolo26s_sgd_640_150e/` |
| `runs/detect/agave_maleza_150ep_2026-10-21/yolo26n_campo_640_150e/` | `docs/resultados/agave_maleza_150ep_2026-10-21/yolo26n_campo_640_150e/` |
| `runs/detect/agave_maleza_150ep_opciones34_2026-10-22/yolo26s_sgd_960_150e/` | `docs/resultados/agave_maleza_150ep_opciones34_2026-10-22/yolo26s_sgd_960_150e/` |
| `runs/detect/agave_maleza_150ep_opciones34_2026-10-22/yolo26s_sgd_box9_640_150e/` | `docs/resultados/agave_maleza_150ep_opciones34_2026-10-22/yolo26s_sgd_box9_640_150e/` |
| `runs/detect/agave_maleza_150ep_opciones34_2026-10-22/cross_resolution_evaluation/` | `docs/resultados/agave_maleza_150ep_opciones34_2026-10-22/cross_resolution_evaluation/` |
| `video_predictions/conteo_maleza_2026-10-26/` | `docs/resultados/conteo_maleza_2026-10-26/` |

[El manifiesto](manifest.json) enumera cada archivo, su ruta de origen, tamaño y SHA-256. Los archivos de origen permanecen intactos en esta computadora.

## Qué contiene cada experimento

Cada una de las cuatro corridas incluye `results.csv` (métricas de entrenamiento y validación por época), `results.png` y `args.yaml` (parámetros efectivos originales). Las carpetas `evaluation/val` y `evaluation/test` contienen las curvas de precisión, recall, F1 y precisión-recall, además de las matrices de confusión. Las evaluaciones cruzadas a 960 se guardan aparte con sus nombres originales.

Los valores agregados, protocolos, selección de checkpoints y verificaciones se conservan en [benchmark](../../benchmark/). Consultar los informes de [los primeros dos modelos](../RESULTADOS_150_EPOCAS_2026-10-22.md) y [la comparación de los cuatro](../COMPARACION_CUATRO_MODELOS_150_EPOCAS_2026-10-22.md) para interpretar las cifras. No mezclar las métricas por época con las evaluaciones independientes de `best.pt` ni comparar el test histórico con el nuevo como si fueran el mismo conjunto.

## Conteo en video

El [LEEME original del 26 de octubre](conteo_maleza_2026-10-26/LEEME.md) describe la ejecución completa en la computadora de cálculo. Esta copia incluye `verificacion.json` y, para cada clip, `cruces.csv`, `cruces.json`, `inferencia.json`, `predicciones.jsonl` y `resumen_final.jpg`. Permite consultar los eventos y sus observaciones por fotograma sin los videos.

Los MP4, las imágenes de cada cruce y los montajes mencionados en el LEEME original permanecen solamente en `video_predictions/conteo_maleza_2026-10-26/` de la computadora de cálculo. Los conteos de 35 y 139 son cruces automáticos por ID, sin validación manual completa; los clips tampoco son un test independiente del dataset.

## Uso de las copias

Los YAML y JSON conservan las rutas absolutas registradas durante la ejecución como información de procedencia. No son rutas portables para lanzar entrenamientos desde otra computadora. Los pesos, datasets, videos y salidas completas permanecen fuera de Git.

Esta carpeta es una captura de los resultados disponibles, no se sincroniza sola con `runs/` o `video_predictions/`. Al publicar nuevos experimentos, agregar sus copias y actualizar el manifiesto desde la computadora de cálculo; conservar las cifras originales para la redacción.
