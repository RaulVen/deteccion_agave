# Insumos para paper - deteccion y conteo de agave joven

## Titulo sugerido

Field Agave Detection and Line-Crossing Count from RGB Video Using YOLO26

## Tesis del paper

Se presenta un flujo reproducible para detectar agaves jovenes en imagenes RGB de campo, seleccionar el mejor modelo YOLO26 entre 11 corridas y demostrar una prueba operacional de tracking/conteo por cruce de linea en video. El resultado debe redactarse como avance de vision computacional para un futuro sistema deshierbador, no como deteccion completa de maleza.

## Fuente de datos y verificacion Roboflow

- Roboflow vivo verificado: `raul-stlme/agave-vty65`, nombre del proyecto `agave`.
- El `data.yaml` local conserva `raul-stlme/raul-stlme`, pero Roboflow devuelve `raul-stlme/agave-vty65` como ID real.
- Roboflow proyecto: 404 imagenes, splits `train=295`, `valid=73`, `test=36`, clase `agave`.
- Roboflow resumen de proyecto: 4374 anotaciones `agave`.
- Roboflow busqueda imagen-por-imagen: 404 imagenes y 4373 anotaciones.
- Export local usado para entrenamiento/evaluacion: 404 imagenes y 4371 cajas YOLO.
- Deriva localizada: `captura_001_corto_f00004_t0000-27s.jpg` tiene 9 cajas en export local y 11 en Roboflow vivo.
- Version viva `1`: 699 imagenes generadas, con resize/stretch a 640 y aumentacion de entrenamiento; no corresponde al benchmark local usado para el paper.
- Todas las imagenes locales son RGB `2880x1620`; no se encontro calibracion de camara ni GSD, por lo que el paper no debe convertir pixeles a unidades fisicas.

## Dataset local usado en el benchmark

| Split | Imagenes | Cajas | Media cajas/imagen | P50 | P95 |
|---|---:|---:|---:|---:|---:|
| Train | 295 | 3175 | 10.76 | 11.0 | 18.0 |
| Val | 73 | 793 | 10.86 | 11.0 | 19.4 |
| Test | 36 | 403 | 11.19 | 10.5 | 17.0 |
| Total | 404 | 4371 | 10.82 | 11.0 | 18.0 |

Distribuciones completas en `docs/evidencia/estadisticas_agave_tesis.json`:

- Cajas/imagen: media 10.819, desviacion 4.405, CV 0.407, min 1, P25 8, P50 11, P75 13, P95 18, max 28.
- Ancho bbox normalizado: media 0.0860, desviacion 0.0449, CV 0.522, P50 0.0750, P95 0.1729.
- Alto bbox normalizado: media 0.1782, desviacion 0.1135, CV 0.637, P50 0.1420, P95 0.4272.
- Area bbox normalizada: media 0.01894, desviacion 0.02200, CV 1.161, P50 0.01043, P95 0.06193.
- Aspecto ancho/alto: media 0.5519, desviacion 0.2435, CV 0.441, P50 0.5213, P95 0.9307.

## Sanity checks

- Clase unica esperada `agave`: verdadero.
- Todas las cajas dentro de limites normalizados: verdadero.
- Todas las imagenes locales son `2880x1620`: verdadero.
- No hay imagenes locales `640x640`: verdadero.
- Pares potencialmente duplicados IoU > 0.90: 0.
- Pares potencialmente duplicados IoU > 0.80: 0.
- Max IoU por imagen: media 0.096, P50 0.088, P95 0.199, max 0.699.
- Dominio/alcance: el dataset actual es una sola clase; maleza queda como trabajo futuro.

## Entrenamiento y mejor modelo

Mejor corrida: `yolo26s_sgd_cos_slow_120e`.

Configuracion:

- Base: `yolo26s.pt`.
- Imagen de entrenamiento: `imgsz=640`.
- Batch: 8.
- Epocas configuradas: 120; early stopping/patience 30.
- Epocas registradas: 86.
- Mejor epoca por benchmark y por curva de validacion: 56.
- Optimizador: SGD.
- Learning rate inicial: 0.005.
- Cosine LR: true.
- Augmentacion de entrenamiento local: flips horizontal/vertical 0.5, escala 0.35, shear 2, perspective 0.0005, mixup 0.05, erasing 0.15, mosaic 0.0.

Metricas test del mejor modelo:

- Precision: 0.693.
- Recall: 0.615.
- mAP50: 0.654.
- mAP50-95: 0.213.

Distribucion de 11 corridas:

- Precision test: media 0.6075, desviacion 0.0654, CV 0.1077, min 0.431, P50 0.622, max 0.693.
- Recall test: media 0.5408, desviacion 0.0530, CV 0.0980, min 0.407, P50 0.539, max 0.615.
- mAP50 test: media 0.5691, desviacion 0.0696, CV 0.1223, min 0.370, P50 0.589, max 0.654.
- mAP50-95 test: media 0.1838, desviacion 0.0271, CV 0.1477, min 0.109, P50 0.192, max 0.213.

Interpretacion clave: el mejor modelo lidera el benchmark, pero el mAP50-95 bajo frente a mAP50 indica margen de mejora en localizacion fina, especialmente importante para actuacion mecanica.

## Tracking y conteo

- Segmento de video: 30 s, intervalo 01:30 a 02:00 del video `3.mp4`.
- Tracker: BoT-SORT configurado localmente en `configs/tracking/botsort_agave.yaml`.
- Parametros: `conf=0.30`, `iou=0.40`, `imgsz=640`, linea horizontal al 50% del frame, direccion `down`, IDs unicos.
- CSV: `video_predictions/3_segment_01m30s_02m00s_tracking_line50_down_unique.csv`.
- Eventos/cruces: 41.
- IDs unicos: 41.
- Conteo final: 41 agaves.
- Primer cruce: 0.400 s; ultimo cruce: 29.994 s; media temporal: 14.899 s.

## Figuras disponibles

Figuras en espanol: `docs/evidencia/figuras/`.
Figuras en ingles para el paper: `docs/evidencia/figuras_en/`.

1. `fig01_overlay_verificacion_agave.png`: overlay de etiquetas YOLO.
2. `fig02_distribucion_dataset.png`: imagenes, cajas y cajas/imagen por split.
3. `fig03_geometria_bboxes.png`: ancho, alto, aspecto y area de cajas.
4. `fig04_benchmark_modelos.png`: mAP50 y mAP50-95 por corrida.
5. `fig05_precision_recall_experimentos.png`: trade-off precision/recall por corrida.
6. `fig06_curvas_entrenamiento_mejor_modelo.png`: curvas del mejor entrenamiento.
7. `fig07_sanity_checks.png`: validaciones de etiquetas e IoU duplicado.
8. `fig08_tracking_conteo.png`: frame final y conteo acumulado.
9. `fig09_versionado_roboflow_local.png`: deriva Roboflow/export local.

## Referencias que se pueden citar

Usar solo las referencias de `docs/paper/referencias_verificadas.md`:

- Jocher et al. (2026), YOLO26, DOI `10.48550/arXiv.2606.03748`.
- Padilla et al. (2021), metricas de deteccion, DOI `10.3390/electronics10030279`.
- Bewley et al. (2016), SORT, DOI `10.1109/ICIP.2016.7533003`.
- Zhang et al. (2022), ByteTrack, DOI `10.1007/978-3-031-20047-2_1`.
- Kamilaris and Prenafeta-Boldu (2018), deep learning in agriculture, DOI `10.1016/j.compag.2018.02.016`.
- Hasan et al. (2021), weed detection survey, DOI `10.1016/j.compag.2021.106067`.

## Limitaciones obligatorias

- El conjunto actual tiene solo la clase `agave`; no evalua aun deteccion de maleza.
- No hay GSD ni calibracion de camara; no reportar diametros, distancias o areas metricas.
- Roboflow vivo y export local tienen deriva de versionado pequena; los resultados del paper usan el export local que produjo el benchmark.
- Test set pequeno: 36 imagenes y 403 cajas; las metricas deben interpretarse como evidencia preliminar.
- El conteo de 41 agaves no tiene ground truth manual frame-a-frame incluido; debe tratarse como prueba operacional reproducible, no como exactitud de conteo validada externamente.

## Comandos de reproducibilidad

```powershell
.\.venv\Scripts\python.exe src\analisis_extendido.py --env-file "C:\Users\iceve\Documents\Codex\2026-07-16\puedes-clonar-este-repositorio-precision-agricola\conference_papares\.env"
.\.venv\Scripts\python.exe src\analisis_agave_tesis.py --lang es
.\.venv\Scripts\python.exe src\figuras_en.py
```
