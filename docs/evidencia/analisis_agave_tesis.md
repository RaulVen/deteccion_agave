# Analisis reproducible - deteccion de agave joven

## Fuente viva y alcance

- Proyecto Roboflow vivo verificado: `raul-stlme/agave-vty65` (nombre `agave`).
- Roboflow proyecto: 404 imagenes, splits {'valid': 73, 'test': 36, 'train': 295}, clases {'agave': 4374}.
- Busqueda viva imagen-por-imagen: 404 imagenes y 4373 anotaciones.
- Export local usado para entrenamiento: 404 imagenes y 4371 cajas YOLO.
- Advertencia: `datasets/yolo26/data.yaml` conserva el slug `raul-stlme/raul-stlme`, pero Roboflow devuelve `raul-stlme/agave-vty65` como ID real del proyecto.
- Advertencia: la version viva `1` reporta 699 imagenes generadas; el benchmark local no usa esa version aumentada.
- Deriva localizada: 1 imagen con conteo distinto entre Roboflow vivo y export local.

## Dataset local

- `train`: 295 imagenes, 3175 cajas, media 10.76 cajas/imagen.
- `val`: 73 imagenes, 793 cajas, media 10.86 cajas/imagen.
- `test`: 36 imagenes, 403 cajas, media 11.19 cajas/imagen.
- Todas las imagenes locales tienen dimension 2880x1620.
- Ancho de caja medio: 0.0860; alto medio: 0.1782; area media: 0.0189.

## Mejor modelo

- Corrida: `yolo26s_sgd_cos_slow_120e` con base `yolo26s.pt`.
- Test: precision=0.693, recall=0.615, mAP50=0.654, mAP50-95=0.213.
- Epocas corridas: 86; mejor epoca segun benchmark: 56.

## Tracking

- Segmento con tracking: 41 cruces/eventos y 41 IDs unicos.
- Conteo final reportado: 41 agaves en direccion `down`.

## Sanity checks

- Clase unica `agave`: True.
- Cajas dentro de limites normalizados: False.
- Pares potencialmente duplicados IoU>0.90: 0; IoU>0.80: 0.
- GSD/calibracion fisica: no se infiere. El analisis reporta desempeno de deteccion y conteo en pixeles/frames, no dimensiones metricas de planta.

## Figuras

- `fig01_overlay_verificacion_agave.png`: overlay de etiquetas locales.
- `fig02_distribucion_dataset.png`: imagenes, cajas y cajas/imagen por particion.
- `fig03_geometria_bboxes.png`: distribuciones de ancho, alto, aspecto y area.
- `fig04_benchmark_modelos.png`: comparacion de mAP por corrida.
- `fig05_precision_recall_experimentos.png`: trade-off precision/recall.
- `fig06_curvas_entrenamiento_mejor_modelo.png`: curvas del mejor entrenamiento.
- `fig07_sanity_checks.png`: validaciones de etiquetas e IoU duplicado.
- `fig08_tracking_conteo.png`: frame final y conteo acumulado.
- `fig09_versionado_roboflow_local.png`: deriva Roboflow/export local.
