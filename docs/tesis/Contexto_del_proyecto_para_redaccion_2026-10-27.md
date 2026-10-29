# Contexto del proyecto para la redacción de la tesis

**Fecha de corte: 27 de octubre de 2026.** Este documento reúne los avances comprobados en archivos locales para mantener este chat dedicado al escrito. Distingue los resultados históricos, los nuevos experimentos con maleza y el prototipo embebido. Las cifras proceden de auditorías documentales; no se realizaron entrenamientos, conexiones a la Raspberry ni nuevas pruebas de campo durante esta revisión.

## 1. Enfoque y estado real del proyecto

La tesis se orienta a **identificar y localizar agaves mediante visión artificial como base perceptiva para un deshierbador autónomo que evite dañarlos o cortarlos**. El objeto detectado es el agave. La maleza constituye el entorno que dificulta reconocerlo; no se ha incorporado como segunda clase del detector.

Hasta la fecha existen tres avances relacionados: modelos YOLO26 evaluados sobre imágenes, demostraciones de seguimiento y conteo en videos, y un prototipo de captura e inferencia local en Raspberry Pi con un modelo histórico. Todavía no está demostrada la protección física del cultivo mediante un mecanismo real. No detectar un agave tampoco demuestra que la región sea maleza o que resulte segura para cortar.

Una formulación fiel para el escrito es: «Se desarrolló un sistema de percepción visual para detectar agaves en escenas agrícolas con presencia de maleza, como base para su protección durante el deshierbe autónomo». La integración mecánica y las condiciones necesarias para prevenir daño deben conservarse como objetivos o validaciones pendientes, según el alcance definitivo.

## 2. Etapa histórica: datos, modelos y conteo

El benchmark histórico utilizó **404 imágenes y 4371 cajas**, con 295 imágenes de entrenamiento, 73 de validación y 36 de prueba. Contiene una clase, `agave`, e imágenes originales de 2880 × 1620 píxeles. La versión aumentada de 699 imágenes registrada en Roboflow es diferente y no fue la entrada de ese benchmark local.

Se documentaron once corridas, incluida una prueba rápida de tres épocas. La mejor configuración observada fue `yolo26s_sgd_cos_slow_120e`: 120 épocas previstas, 86 realizadas y mejor checkpoint en la época 56. Sobre el test histórico obtuvo precisión **69.30%**, recall **61.50%**, mAP50 **65.40%** y mAP50-95 **21.30%**. El CSV original ya contiene estos resultados redondeados.

El seguimiento histórico con BoT-SORT produjo **41 cruces descendentes** de IDs únicos en un fragmento de 30 segundos de `3.mp4`, entre 01:30 y 02:00. Otro CSV archivado contiene **83 eventos e IDs distintos** en un fragmento de 60 segundos. Son resultados automáticos; no existe una referencia manual completa que permita convertirlos en exactitud de conteo.

Estos antecedentes se deben presentar como una etapa del proyecto. Comparar directamente sus métricas con las nuevas no permite medir el efecto de agregar maleza: cambiaron el test, los datos de entrenamiento y otras condiciones experimentales.

## 3. Ampliación del dataset con escenas de maleza

La exportación nueva aportó **1826 imágenes, 10180 cajas y 47 etiquetas vacías**, procedentes del proyecto Roboflow `agave-maleza`, versión 1. Se integró con la base histórica en la versión local `agave_maleza_2026-10-21`.

| Partición combinada | Imágenes | Cajas de agave | Etiquetas vacías | Históricas | Nuevas |
|---|---:|---:|---:|---:|---:|
| Entrenamiento | 1493 | 9529 | 38 | 295 | 1198 |
| Validación | 435 | 2967 | 9 | 73 | 362 |
| Prueba | 136 | 1115 | 0 | 36 | 100 |
| Reserva | 166 | 940 | 0 | 0 | 166 |
| Total preservado | 2230 | 14551 | 47 | 404 | 1826 |

Se emplearon **2064 imágenes activas y 13611 cajas**. Las 166 reservas quedaron fuera de entrenamiento y evaluación. Se preservó la resolución original de 2880 × 1620; 640 y 960 representan tamaños de procesamiento. La auditoría volvió a contar las imágenes y etiquetas; todos los identificadores de clase encontrados fueron `0`, correspondiente a agave.

La partición aleatoria original de las imágenes nuevas se sustituyó por grupos de clips: v02–v07 y v11–v16 para entrenamiento; v08–v10 para validación; v17–v19 para prueba. Ningún clip nuevo se reparte entre conjuntos activos. Se reservaron guardas temporales de 60 segundos alrededor de sus fronteras.

La preparación informó ausencia de duplicados exactos de píxeles, pero eso no garantiza independencia espacial: los videos nuevos pertenecen a una misma salida de campo y pueden contener revisitas. Además, se conservaron las particiones históricas, cuyos cuatro videos de origen aparecen en entrenamiento, validación y prueba. El manifiesto contiene, por ejemplo, fotogramas consecutivos de `captura_001_corto` en entrenamiento y prueba. Esto documenta proximidad temporal y riesgo de correlación; no permite cuantificar su efecto sobre las métricas.

La revisión manual disponible cubrió doce imágenes y señaló dos casos pendientes: posibles agaves sin etiqueta y una hoja parcial en una imagen negativa. Las campañas conservaron esas anotaciones. **No hay etiquetado sistemático seca/húmeda ni resultados separados por humedad.** El test tampoco contiene imágenes negativas, por lo que no caracteriza el comportamiento en escenas completamente carentes de agaves.

## 4. Cuatro entrenamientos nuevos y resultados

Las campañas del 21–22 de octubre completaron cuatro entrenamientos de **150 épocas**, partiendo de pesos preentrenados. Se mantuvieron semilla 26, batch efectivo 8, ausencia de parada temprana e inversión vertical desactivada. Se conservaron aumentos de iluminación y otros aumentos de campo. YOLO26s usó SGD con tasa inicial 0.005 y calendario coseno; el modo `auto` de YOLO26n eligió AdamW con tasa inicial 0.002.

El entrenamiento se ejecutó en una **NVIDIA GeForce RTX 5050 Laptop GPU**, con Python 3.12.9, Ultralytics 8.4.57 y PyTorch 2.10.0+cu128. Estas condiciones no corresponden a la Raspberry Pi. Se comprobaron las 150 épocas y los hashes de `best.pt`, `last.pt` y `results.csv` de las cuatro corridas.

Los checkpoints se eligieron mediante validación. La siguiente tabla usa el mismo test de 136 imágenes y 1115 cajas, evaluado a 640; las métricas son porcentajes. La última columna corresponde a la reevaluación de validación, no al valor registrado durante la época de entrenamiento.

| Configuración entrenada | Mejor época | Precisión test | Recall test | mAP50 test | mAP50-95 test | mAP50-95 val |
|---|---:|---:|---:|---:|---:|---:|
| YOLO26s SGD, 640, box=7.5 | 23 | 68.20 | 62.52 | 66.55 | 24.32 | 38.33 |
| YOLO26s SGD, 640, box=9.0 | 11 | 70.07 | 62.06 | 68.34 | 24.27 | 37.94 |
| YOLO26n AdamW, 640 | 48 | 67.63 | 51.71 | 58.61 | 22.23 | 37.69 |
| YOLO26s SGD, 960 | 20 | 64.91 | 52.47 | 57.69 | 20.94 | 35.45 |

El protocolo común usó `conf=0.001`, `iou=0.7`, `max_det=300`, `rect=true`, sin aumentos de evaluación. El umbral para construir curvas no representa necesariamente el umbral operativo de un video. Las cifras agregadas de precisión y recall no garantizan la misma ventaja entre modelos cuando se fija un umbral operativo común.

La referencia para pruebas posteriores fue **YOLO26s SGD a 640, box=7.5**, por su mayor mAP50-95 y recall en esa comparación. `box=9.0` elevó precisión y mAP50, pero no mAP50-95 ni recall. La comparación Nano/Small también cambia optimizador y calendario; no aísla exclusivamente el tamaño de la red.

Se evaluaron adicionalmente dos checkpoints a ambas resoluciones:

| Entrenamiento/selección | Evaluación | Recall test | mAP50 test | mAP50-95 test |
|---:|---:|---:|---:|---:|
| 640 | 640 | 62.52 | 66.55 | 24.32 |
| 640 | 960 | 62.06 | 65.53 | 22.36 |
| 960 | 640 | 52.47 | 57.69 | 20.94 |
| 960 | 960 | 60.63 | 66.98 | 24.67 |

960/960 logró el mayor mAP50-95 observado, con solo **0.35 puntos porcentuales** de ventaja sobre 640/640 y menor recall. Una corrida por configuración no demuestra superioridad estadística. No se midió aquí velocidad de despliegue mediante un protocolo dedicado.

Las cuatro curvas muestran caída de validación tras máximos tempranos, compatible con sobreajuste. Completar 150 épocas no significa usar la época 150: los resultados finales corresponden a `best.pt`. No debe confundirse la selección de época por validación con el ranking descriptivo de configuraciones observado en test.

## 5. Demostraciones nuevas en video

El 26 de octubre se utilizó el nuevo YOLO26s SGD a 640, checkpoint de la época 23, en escritorio con CUDA. Una demostración sin seguimiento procesó 60 segundos y 900 cuadros de un video fuente de validación; no constituye prueba externa.

Los conteos emplearon BoT-SORT, confianza 0.30, entrada 640, `rect=false`, FP32 y seguimiento persistente. Se contó el centro de caja que cruzaba hacia abajo una línea horizontal al 50%, una vez por ID. El tracker se reinició en cada fragmento. La presentación a 1280 × 720 se generó después de inferir sobre el cuadro fuente.

| Fragmento | Intervalo | Duración | Cuadros | Eventos / IDs | Procedencia |
|---|---|---:|---:|---:|---|
| anterior_0100_0136 | 01:00–01:36 | 36 s | 540 | 35 / 35 | v08, validación |
| nuevo_0102_0320 | 01:02–03:20 | 138 s | 2070 | 139 / 139 | v04, entrenamiento |

Los CSV y JSON coinciden en los totales. No hay conteo manual completo, ni garantía de que cada ID represente una planta física distinta. En el fragmento largo existen cuatro cruces interpolados entre observaciones separadas por más de un segundo; requieren revisión manual. Estos resultados demuestran funcionamiento del flujo de seguimiento, no exactitud perfecta, generalización ni protección del cultivo.

## 6. Prototipo embebido: avance independiente

La última implementación documentada en Raspberry Pi 4 de 2 GB utilizó el **modelo histórico**, no los nuevos pesos de octubre. El benchmark aislado del 21 de septiembre midió 60 inferencias en diez imágenes, después del calentamiento, a entrada 320: tiempo medio **1.07 s**, equivalente a **0.94 imágenes/s**, pico de memoria 482 MiB y temperatura máxima **74.98 °C**. Excluyó captura RTSP, interfaz y conteo; duró aproximadamente dos minutos.

El 9 de octubre se exportó ese mismo modelo a **NCNN con pesos en FP32, entrada de 320 × 320 y ejecución en CPU**, y se separaron captura, inferencia y presentación. Esa descripción no certifica la precisión interna de todas las operaciones del motor. La exportación desactivó la rama end-to-end y aplicó NMS; no debe asumirse equivalencia exacta con el `.pt`. La comparación sobre diez imágenes fue exploratoria, no una validación completa del modelo exportado.

Las muestras del sistema completo registraron video cercano a 15 fps y detección entre aproximadamente **1.30 y 2.69 inferencias/s**, bajo condiciones distintas de alimentación y ejecución. No forman un benchmark controlado ni prueban funcionamiento sostenido durante horas. La tasa de video no equivale a la tasa del detector.

El contador embebido asocia centros por distancia; **no usa BoT-SORT**. Se documentaron operación local con internet bloqueado y LAN disponible, restauración del visor y pruebas de red. La conexión física directa cámara–Raspberry sin router y el conteo con plantas en movimiento no quedaron plenamente validados. No se encontró despliegue de los nuevos pesos ni accionamiento real de corte en los respaldos revisados.

## 7. Pendientes y organización del escrito

Antes de afirmar protección efectiva faltan calibración cámara–herramienta, definición del área protectora, medición de latencias completas, integración con actuadores y pruebas de daño. También quedan por documentar condiciones seca/húmeda, revisión sistemática de etiquetas, test con negativos, evaluación externa por campo o fecha, repetición de configuraciones y exactitud del seguimiento frente a anotación manual. Un recall de 62.52% no representa una tasa de protección.

El capítulo 2 puede fundamentar visión RGB, detección de una clase, CNN y YOLO26, transferencia de aprendizaje, métricas, sobreajuste, particiones, seguimiento, inferencia embebida y relación entre percepción y control. Los tamaños de datasets y protocolos pertenecen principalmente a metodología; las tablas numéricas, a resultados. Este contexto no reemplaza las referencias científicas ni demuestra por sí mismo afirmaciones teóricas.

## 8. Evidencia esencial para futuras revisiones

- [Datos y recuentos](../../datasets/prepared/agave_maleza_2026-10-21/summary.json) y [manifiesto por imagen](../../datasets/prepared/agave_maleza_2026-10-21/manifest.csv).
- [Benchmark histórico](../../benchmark/agave_benchmark.csv).
- [Campaña nueva inicial](../../benchmark/agave_maleza_150ep_2026-10-21/agave_benchmark.csv), [opciones 3 y 4](../../benchmark/agave_maleza_150ep_opciones34_2026-10-22/agave_benchmark.csv) y [evaluación cruzada](../../benchmark/agave_maleza_150ep_opciones34_2026-10-22/cross_resolution_benchmark.csv).
- [Conteos del 26 de octubre](../resultados/conteo_maleza_2026-10-26/LEEME.md).
- [Benchmark Raspberry](../../hardware/raspberry/benchmark/RESULTADO.md) y [mejoras del prototipo](../../hardware/raspberry/restore/MEJORAS_CAMPO.md).
- Auditorías detalladas: [modelos y datos](notas/auditoria_modelos.md) y [despliegue, video y conteo](notas/auditoria_embebido.md).
