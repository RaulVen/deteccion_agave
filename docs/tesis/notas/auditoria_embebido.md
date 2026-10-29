# Auditoría documental de despliegue, video y conteo

Fecha de revisión: 27 de octubre de 2026. Revisión de solo lectura de los respaldos locales; no se conectó a dispositivos, no se reentrenaron modelos ni se ejecutaron pruebas de campo. No se encontraron archivos AGENTS.md en las carpetas y ascendientes inspeccionados. Se omiten direcciones de red y configuración privada.

## Conclusión para el escrito

La evidencia demuestra dos líneas de avance relacionadas pero todavía distintas: (a) un prototipo embebido de captura, detección y visualización en Raspberry Pi con el modelo histórico, exportado a NCNN a 320 × 320; y (b) nuevos entrenamientos y demostraciones de detección, seguimiento y conteo en videos con maleza usando los pesos del 21–22 de octubre, ejecutados con CUDA a entrada 640. No hay evidencia en los respaldos revisados de que los nuevos pesos se hayan desplegado en la Raspberry o se hayan conectado a un actuador real de corte. El conteo es un resultado auxiliar de seguimiento, no una validación de protección física del agave.

## Cronología y cifras verificables

| Fecha o etapa | Evidencia | Resultado y límites |
|---|---|---|
| Histórico de junio | CSV de video y documentación histórica | Segmento de 30 s de `3.mp4`, 01:30–02:00: 41 cruces descendentes y 41 IDs únicos. Sin conteo manual completo que permita medir exactitud. |
| Histórico adicional | CSV `captura_000_segment_00m45s_01m45s_tracking_line50_down_unique.csv` | 83 filas y 83 IDs distintos, dirección descendente, intervalo de 60 s según nombre del archivo. Es evidencia adicional archivada; no se encontró un manifiesto equivalente al de octubre que documente todos los parámetros y pesos. La fecha del archivo es 26-junio, pero una fecha de modificación por sí sola no certifica fecha de experimento. |
| 21-septiembre | `rpi_benchmark/RESULTADO.md` y `results_threads4.json` | YOLO26s histórico en Raspberry Pi 4 de 2 GB: 60 inferencias medidas en 10 imágenes tras 3 de calentamiento; media 1.0657 s, 0.9384 imágenes/s; pico RSS 482 MiB; máximo 74.984 °C; swap 0 y sin throttling reportado al finalizar. Inferencia aislada, sin RTSP, interfaz ni conteo. |
| 9-octubre | `rpi_restore/RESTAURACION.md` | Restauración de visor, búsqueda de cámara, línea movible, registros de cruce y accesos iniciar/detener. Video e inferencia comprobados en una habitación sin agaves; conteo con plantas en movimiento no validado. |
| 9-octubre | `MEJORAS_CAMPO.md`, JSON y código | Exportación del mismo peso histórico a NCNN FP32 320 × 320, ejecución directa NCNN con dos hilos, captura continua, inferencia en proceso independiente y dibujo con Pygame/SDL. Video cerca de 15 fps; detector entre aproximadamente 1.3 y 2.7 inferencias/s en muestras distintas, con distintas condiciones de alimentación. No se deben combinar como un benchmark controlado. |
| 9-octubre | `ETHERNET_DIRECTO.md`, `RESPALDO_MEMORIA_NUEVA.md` | Red local para campo y prueba virtual de DHCP; video/inferencia sin internet demostrados mediante bloqueo de internet manteniendo LAN. La conexión física directa cámara–Raspberry sin router figura pendiente de verificación. |
| 21–22-octubre | Documentos de resultados y benchmark | Nuevos modelos entrenados sobre datos originales y escenas con maleza; 4 configuraciones, 150 épocas cada una. Referencia YOLO26s SGD a 640, mejor época 23. Estos resultados son de detección en imágenes, no de operación mecánica ni de velocidad embebida. |
| 26-octubre | `video_predictions/maleza_2005_yolo26s_640_2026-10-26` | Demostración de detección sin tracking de 60 s, 900 cuadros a 15 fps, del nuevo YOLO26s. Video fuente aportó imágenes de validación; no prueba independiente. |
| 26-octubre | `video_predictions/conteo_maleza_2026-10-26` | Dos fragmentos con BoT-SORT y línea al 50%: 35 cruces en 36 s y 139 cruces en 138 s. Totales y eventos coinciden en CSV/JSON y verificación guardada. Sin referencia manual. |

## Raspberry: modelo y condiciones

El peso histórico es `yolo26s_sgd_cos_slow_120e/weights/best.pt`, SHA256 `A847C3E25D4AF7B6AC8B78033F5A268034D67B621DFBCB61456BA33E454F2C0A`. El nombre incluye 120 épocas configuradas; la documentación histórica informa 86 realizadas y mejor época 56. No es el nuevo `yolo26s_sgd_640_150e`.

El benchmark del 21 de septiembre utilizó Raspberry Pi 4 Model B Rev 1.5 de 2 GB, Debian 13 ARM64, PyTorch 2.6.0+debian, Ultralytics 8.4.90 y OpenCV 4.10.0. CPU, `imgsz=320`, confianza 0.20, IoU 0.40, lote 1. Las imágenes se redujeron previamente a 640 × 360; esa reducción y lectura no están dentro del tiempo `predict`. Se solicitaron 4 hilos pero Ultralytics reajustó a 3. La primera llamada tardó 7.08 s y no se incluyó en la media. La medición duró unos dos minutos: no demuestra estabilidad térmica de horas de campo.

La exportación del 9 de octubre conserva ese peso; no es reentrenamiento. Su `metadata.yaml` declara una clase `agave`, entrada 320 × 320, `end2end: false`. El exportador deshabilitó la rama end-to-end y se aplica NMS, por lo que no se debe afirmar equivalencia exacta entre `.pt` y NCNN.

En 10 imágenes, a confianza 0.20 e IoU de matching 0.50, el `.pt` obtuvo TP=52, FP=32, FN=70, precisión 0.619 y recall 0.426; NCNN TP=56, FP=22, FN=66, precisión 0.718 y recall 0.459. Es una muestra reducida a umbral fijo; no es mAP ni validación total. Además, el padding efectivo de PyTorch puede ser rectangular y NCNN es cuadrado fijo. El motor NCNN directo produjo igual número de detecciones que Ultralytics+NCNN en esas diez imágenes, con diferencia numérica máxima menor que 0.0002.

La comparación exploratoria de tiempos (2.77 s/imagen PyTorch; 0.51 s Ultralytics+NCNN; 0.70 s motor NCNN directo de dos hilos) estuvo afectada por alimentación inestable, según el propio registro. No permite atribuir de forma controlada una aceleración determinada al formato.

Se distinguen las muestras guardadas del sistema completo:

- `offline_performance.json`: 9-octubre 17:34:44, video 15.04 fps, presentación 14.94 fps, detección 1.30 inferencias/s, última inferencia 0.777 s y antigüedad del cuadro recibido 0.093 s.
- `desktop_performance.json`: 17:36:27, video 12.66 fps, presentación 14.96 fps, detección 2.09 inferencias/s, inferencia 0.406 s y antigüedad 0.080 s.
- `MEJORAS_CAMPO.md` contiene otras muestras cercanas, incluida detección 1.29 inferencias/s con bajo voltaje y throttling activos; no son las mismas marcas de tiempo de los dos JSON.
- `RESPALDO_MEMORIA_NUEVA.md` documenta en la memoria nueva video 14.97 fps, detección 2.69 inferencias/s e inferencia 0.358 s con internet bloqueado. Se reporta `get_throttled=0x0` durante la prueba de esa memoria. No hay JSON local de esa muestra junto al informe.

La tasa de presentación del video no es la tasa del detector. La antigüedad del último cuadro recibido no mide la latencia completa desde el sensor ni hasta el actuador. Las diferencias entre muestras no deben atribuirse al acceso a internet.

## Seguimiento embebido frente a seguimiento de escritorio

El respaldo `rpi_live_infer_display.py`, clase `LineCounter` (línea 110), asocia detecciones por distancia euclidiana entre centros, con distancia máxima predeterminada 110 píxeles y TTL 8 actualizaciones de inferencia. Registra un cruce cuando cambia el lado del centro respecto a la línea, una vez por ID; en ese respaldo no restringe a dirección descendente. No utiliza BoT-SORT. Genera eventos JSONL con coordenadas, confianza, ID y número de inferencia. No se encontró código de accionamiento GPIO, UART, PWM o corte dentro de este visor.

Las pruebas históricas y de octubre en escritorio sí emplean `configs/tracking/botsort_agave.yaml`. Esa configuración contiene `track_high_thresh=0.25`, `track_low_thresh=0.1`, `new_track_thresh=0.25`, `track_buffer=90`, `match_thresh=0.8`, compensación de movimiento `sparseOptFlow` y `with_reid=False`. No debe describirse como reconocimiento por apariencia entrenado/ReID activo.

## Demostraciones nuevas del 26 de octubre

Los `inferencia.json` identifican los pesos nuevos con SHA256 `aef8bce09a9c76ae5ec0f30e2ef2f2958d681715e563fe9b4927399d827f28e7`. Se usó `best.pt` de YOLO26s + SGD entrenado a 640, campaña `agave_maleza_150ep_2026-10-21`, seleccionado en época 23 por validación. No se utilizaron pesos de la época 150.

Parámetros de ambos conteos: `imgsz=640`, `conf=0.30`, `iou=0.70`, `rect=false`, `half=false` (FP32), `max_det=300`, CUDA dispositivo 0, Ultralytics 8.4.57, PyTorch 2.10.0+cu128, `model_end2end=true`, seguimiento persistente. La única clase guardada es `agave`.

El criterio de conteo se conserva: centro de caja que cruza de arriba hacia abajo una línea horizontal al 50%, una vez por ID. El tracker y contador empiezan vacíos en cada fragmento. Aparecer por primera vez debajo de la línea no cuenta. La línea se sitúa en y=810 del original 2880 × 1620; la salida dibujada es 1280 × 720, y=360. El código ejecuta `model.track(frame, ...)` sobre el cuadro original (con preprocesamiento del modelo a 640) antes de `cv2.resize` para exportar el video; 720p es resolución de presentación, no de inferencia.

| Fragmento | Fuente e intervalo | Cuadros | Cruces / IDs contados | Pertenencia de fuente al dataset |
|---|---|---:|---:|---|
| `anterior_0100_0136` | Fuente v08, 01:00–01:36 | 540 | 35 / 35 | Validación |
| `nuevo_0102_0320` | Fuente v04, 01:02–03:20 | 2070 | 139 / 139 | Entrenamiento |

Los CSV fueron leídos en esta auditoría: sus filas coinciden con 35 y 139. `verificacion.json` documenta decodificación completa de los MP4 sin errores y coincidencia de eventos; esta revisión no repitió la decodificación. No son pruebas de generalización independiente porque proceden de la salida de campo que aportó los datos de entrenamiento/validación. No hay conteo manual completo para estimar error absoluto, precisión del conteo, duplicaciones, omisiones ni identidad física real.

En el fragmento corto el intervalo máximo entre observaciones que completan un cruce fue 3 cuadros, 0.20 s. En el largo se verificaron en el CSV cuatro eventos con huecos superiores a 1 s:

| Evento | ID | Separación en cuadros | Separación a 15 fps |
|---:|---:|---:|---:|
| 97 | 503 | 45 | 3.00 s |
| 104 | 540 | 16 | 1.07 s |
| 114 | 575 | 40 | 2.67 s |
| 117 | 589 | 46 | 3.07 s |

El instante de cruce se estima por interpolación entre observaciones. Esos cuatro eventos merecen revisión manual; la persistencia de un ID no garantiza que corresponda a una misma planta física.

La demostración previa sin tracking procesó 900 cuadros (60 s), de v08 en validación, también con confianza 0.30 y entrada 640. Sus detecciones por cuadro variaron de 0 a 12, mediana 4; 257 cuadros sin detecciones. No se deben llamar 257 fallos: algunos cuadros presentan camino o vegetación sin agaves anotados, y no existe verdad de terreno completa por fotograma.

Respecto al histórico de 41 cruces, se mantuvieron confianza 0.30, entrada nominal 640, línea al 50%, dirección descendente y configuración BoT-SORT; cambiaron pesos y escenas, y la nueva ejecución usa `rect=false` explícito e `iou=0.70` frente al `iou=0.40` histórico. El manifiesto registra `model_end2end=true`: no se debe atribuir a ese cambio de IoU una mejora de NMS ni confundirlo con los umbrales de asociación del tracker. No se dispone aquí de una comparación controlada antiguo/nuevo sobre idénticos fragmentos y parámetros.

## Lo que todavía no puede afirmarse en la tesis

1. Que el nuevo detector funciona con una tasa determinada en Raspberry: las cifras embebidas son del peso histórico a entrada 320.
2. Que el deshierbador ya evita daños o realiza corte selectivo: no se encontró verificación de actuadores reales, calibración cámara–herramienta, latencia de parada/corte ni ensayos de daño al cultivo.
3. Que los cuadros de detección representan toda la región física segura de la planta: no se documentó conversión métrica/GSD ni calibración física, y caja no equivale a contorno completo de hojas.
4. Que 35/139/41/83 equivalen a exactitud perfecta o a censos manualmente verificados: son eventos automáticos por ID.
5. Que la prueba sin internet ya verificó físicamente conexión directa sin router: el test guardado bloqueó internet manteniendo LAN; el DHCP directo se probó virtualmente.
6. Que 15 fps del video significa inferencia a 15 fps, o que el tiempo de procesamiento de video incluye toda la carga inicial y representa velocidad de despliegue.
7. Que la presencia de maleza en las imágenes equivale a una segunda clase detectada: los modelos nuevos y las demostraciones siguen teniendo únicamente `agave` como clase objetivo.

## Redacción sugerida, utilizable en el estado actual del proyecto

«Se ha desarrollado un sistema de percepción visual orientado a identificar agaves en escenas de cultivo con presencia de maleza, como base para su protección durante el deshierbe autónomo. El proyecto cuenta con modelos de detección evaluados sobre imágenes, demostraciones de seguimiento y conteo por cruce de línea en videos y un prototipo de inferencia local en Raspberry Pi con una versión histórica del modelo. Las pruebas realizadas aún no validan la protección física de las plantas ni la actuación mecánica, y la transferencia de los nuevos pesos al sistema embebido debe evaluarse de forma específica».

## Fuentes locales principales

Base tesis: `C:/Users/iceve/Documents/ChatGPT/tesis/`.

- `rpi_benchmark/RESULTADO.md` y `results_threads4.json`: benchmark aislado y condiciones.
- `rpi_restore/RESTAURACION.md`: restauración y limitación de prueba sin plantas.
- `rpi_restore/MEJORAS_CAMPO.md`: cambios, comparación de backends y límites.
- `rpi_restore/comparison_summary.json` y `direct_ncnn_comparison.json`: datos de equivalencia exploratoria.
- `rpi_restore/offline_performance.json`, `desktop_performance.json`: muestras puntuales.
- `rpi_restore/RESPALDO_MEMORIA_NUEVA.md`, `ETHERNET_DIRECTO.md`: memoria, modo local y pruebas de red.
- `rpi_restore/best_ncnn_model/metadata.yaml`: formato, tamaño y rama end-to-end desactivada.
- `rpi_restore/rpi_live_infer_display.py:110`: contador ligero por distancia de centros.

Base repositorio: `C:/Users/iceve/Documents/github/deteccion de agave/`.

- `docs/HISTORICO_BENCHMARK.md:110`, `docs/paper/insumos_paper.md`: seguimiento histórico y limitaciones.
- `video_predictions/3_segment_01m30s_02m00s_tracking_line50_down_unique.csv`: 41 eventos.
- `video_predictions/captura_000_segment_00m45s_01m45s_tracking_line50_down_unique.csv`: 83 eventos archivados.
- `docs/COMPARACION_CUATRO_MODELOS_150_EPOCAS_2026-10-22.md`: modelos nuevos, resolución y límites.
- `video_predictions/maleza_2005_yolo26s_640_2026-10-26/LEEME.md` e `inferencia.json`: demostración de detección sin seguimiento.
- `video_predictions/conteo_maleza_2026-10-26/LEEME.md` y `verificacion.json`: demostraciones con conteo.
- `video_predictions/conteo_maleza_2026-10-26/anterior_0100_0136/inferencia.json` y `cruces.csv`: parámetros y 35 eventos.
- `video_predictions/conteo_maleza_2026-10-26/nuevo_0102_0320/inferencia.json` y `cruces.csv`: parámetros y 139 eventos.
- `configs/tracking/botsort_agave.yaml`: configuración de seguimiento.
- `scripts/predict_video_fragment.py:148`: inferencia sobre cuadro fuente; línea 180: reducción para presentación después de inferir.
- `scripts/line_crossing_counter.py:41`: regla de conteo e interpolación.

Observación secundaria: `docs/evidencia/analisis_agave_tesis.md` afirma «Cajas dentro de límites normalizados: False», mientras `docs/paper/insumos_paper.md` afirma verdadero. Es una discrepancia entre resúmenes históricos que conviene resolver contra etiquetas y auditoría de datos antes de reutilizar esa frase; no afecta a las cifras de conteo revisadas aquí.
