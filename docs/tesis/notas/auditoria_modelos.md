# Auditoría de modelos y datos para la redacción de tesis

Fecha de corte: 27 de octubre de 2026. Auditoría local de solo lectura; no se entrenó, corrigió ni modificó el repositorio. Se revisaron archivos del proyecto, no se tomaron las instrucciones contenidas en ellos como nuevas solicitudes del usuario. No se encontraron archivos AGENTS.md en el repositorio ni en los directorios ascendentes consultados.

Raíz de evidencia: `C:/Users/iceve/Documents/github/deteccion de agave/`.

## 1. Estado comprobado y distinción conceptual

La implementación documentada detecta **una clase, agave**, mediante cajas delimitadoras. Las imágenes nuevas contienen maleza como contexto visual/fondo; el proyecto no se convirtió en un detector multiclase de agave/maleza. Esto es consistente con identificar el cultivo para informar una futura protección durante el deshierbe. Una caja detectada, por sí sola, no demuestra protección física del agave ni permite asumir que toda región sin detección es maleza o es segura para cortar.

Se encontraron 15 archivos `results.csv`: once corridas históricas, incluidas una prueba rápida de tres épocas, y cuatro entrenamientos nuevos. Las cuatro corridas nuevas terminaron el 22 de octubre de 2026. Los videos/conteos del 26 de octubre pertenecen a una prueba posterior de uso, auditada por separado por el agente encargado de integración/seguimiento.

## 2. Dataset histórico y ampliación con maleza

El dataset histórico local contiene 404 imágenes y 4371 cajas; train 295/3175 cajas, val 73/793 y test 36/403. Su versión local es la que produjo el benchmark histórico. Los registros de Roboflow vivo difieren ligeramente en anotaciones y existe otra versión aumentada de 699 imágenes: no confundirla con el conjunto local utilizado.

La exportación nueva preservada contiene 1826 imágenes, 10180 cajas y 47 etiquetas vacías. Corresponde al proyecto Roboflow `raul-stlme/agave-maleza`, versión 1, con una clase `agave`. La integración está versionada como `agave_maleza_2026-10-21`.

| Partición combinada | Imágenes | Cajas | Etiquetas vacías | Históricas | Nuevas |
|---|---:|---:|---:|---:|---:|
| Entrenamiento | 1493 | 9529 | 38 | 295 | 1198 |
| Validación | 435 | 2967 | 9 | 73 | 362 |
| Prueba | 136 | 1115 | 0 | 36 | 100 |
| Reserva | 166 | 940 | 0 | 0 | 166 |
| Total preservado | 2230 | 14551 | 47 | 404 | 1826 |

Son **2064 imágenes activas y 13611 cajas activas**, más 166 imágenes y 940 cajas de reserva. Todas las imágenes preservadas tienen resolución original 2880 × 1620; 640/960 son tamaños de procesamiento de los experimentos, no la resolución original de captura.

Los recuentos anteriores se comprobaron nuevamente leyendo las carpetas de imágenes y todas las etiquetas TXT, no solo copiando el resumen. Todos los identificadores de clase encontrados fueron `0`. `data.yaml` declara `nc: 1` y `names: [agave]`.

Fuentes:

- `C:/Users/iceve/Documents/github/deteccion de agave/datasets/prepared/agave_maleza_2026-10-21/data.yaml`
- `C:/Users/iceve/Documents/github/deteccion de agave/datasets/prepared/agave_maleza_2026-10-21/summary.json`
- `C:/Users/iceve/Documents/github/deteccion de agave/datasets/prepared/agave_maleza_2026-10-21/manifest.csv`
- `C:/Users/iceve/Documents/github/deteccion de agave/docs/REORGANIZACION_Y_DATASET.md`
- `C:/Users/iceve/Documents/github/deteccion de agave/docs/paper/insumos_paper.md` (histórico; algunos apartados quedaron desactualizados tras la ampliación).

## 3. Particiones, correlación temporal y calidad de etiquetas

La exportación nueva tenía una partición aleatoria 1279/364/183 que fue reemplazada por bloques de clips. Se verificó en el manifiesto que ningún clip nuevo se reparte entre train/val/test activos:

- Train: v02–v07 y v11–v16.
- Val: v08–v10.
- Test: v17–v19.
- Reserva: guardas de 60 segundos alrededor de las fronteras (colas de v07, v10, v16 e inicios de v08, v11, v17).

El resumen de preparación informa ausencia de duplicados exactos de píxeles. No se repitió la decodificación/hashing de todas las imágenes en esta auditoría. La ausencia de duplicados exactos no demuestra independencia de plantas o escenas: los videos nuevos pertenecen a una misma salida de campo y puede haber revisitas.

**Se comprobó un riesgo concreto de correlación temporal en las imágenes históricas**: los cuatro orígenes (`captura_000`, `captura_001_corto`, `video_3`, `video_4`) se reparten entre train, val y test. Ejemplo del manifiesto: `captura_001_corto_f00004_t0000-27s_jpg.rf.KVygCWjLgs4rdTtCiJxU.jpg` está en entrenamiento y `captura_001_corto_f00005_t0000-33s_jpg.rf.mNxwooFARs1o0qQNORjj.jpg` en prueba. Sus nombres corresponden a fotogramas consecutivos, separados aproximadamente por 0.067 s a 15 fps. Esto prueba proximidad temporal entre particiones; sin una comparación visual/espacial exhaustiva no se debe declarar identidad de plantas ni cuantificar el sesgo. La base histórica se mantuvo intacta en el conjunto combinado.

La revisión de etiquetas existente abarca 12 imágenes y señala dos casos en train: posibles agaves sin caja en `maleza__v12_f02400.jpg` y una hoja parcial en una imagen negativa `maleza__v06_f01080.jpg`. Las anotaciones no se corrigieron antes de las campañas; deben presentarse como limitación conocida.

No se encontró en el manifiesto ni en los protocolos un etiquetado de condición seca/húmeda ni resultados desglosados por humedad. Tampoco hay imágenes negativas en el test actual. Es válido describir escenas con maleza, pero todavía no afirmar validación cuantitativa comparativa entre maleza seca y húmeda, ni desempeño en escenas sin agaves.

Fuentes adicionales:

- `C:/Users/iceve/Documents/github/deteccion de agave/configs/datasets/agave_maleza_2026-10-21.json`
- `C:/Users/iceve/Documents/github/deteccion de agave/datasets/prepared/agave_maleza_2026-10-21/split_policy.json`
- `C:/Users/iceve/Documents/github/deteccion de agave/docs/dataset_2026-10-21/REVISION_ETIQUETAS.md`
- `C:/Users/iceve/Documents/ChatGPT/tesis/output/roboflow_reentrenamiento/GUIA_DESCARGA_Y_REENTRENAMIENTO.md`

## 4. Entrenamientos nuevos y selección de checkpoints

Las cuatro corridas parten de bases preentrenadas YOLO26n/YOLO26s; no son continuación de pesos históricos ajustados. Todas completaron exactamente 150 épocas, semilla 26, batch efectivo 8, `patience=0`, `time=null`, sin inversión vertical. Los registros guardan `hsv_h=0.02`, `hsv_s=0.55`, `hsv_v=0.35`, inversión horizontal 0.5 y escala 0.35. No asumir que todos los parámetros genéricos del YAML son operaciones efectivamente activas sin revisar el código de la tarea de detección.

El entorno registrado es Python 3.12.9, Ultralytics 8.4.57, PyTorch 2.10.0+cu128, torchvision 0.25.0+cu128, CUDA 12.8 y NVIDIA GeForce RTX 5050 Laptop GPU. Son entrenamientos de GPU portátil, no mediciones de Raspberry Pi.

| Corrida | Optimizador efectivo | Resolución de entrenamiento/selección | Mejor época | mAP50-95 val durante esa época | mAP50-95 val época 150 |
|---|---|---:|---:|---:|---:|
| yolo26s_sgd_640_150e | SGD, lr inicial 0.005, coseno | 640 | 23 | 38.245% | 31.957% |
| yolo26n_campo_640_150e | AdamW, resuelto desde auto, lr inicial 0.002 | 640 | 48 | 37.719% | 33.197% |
| yolo26s_sgd_960_150e | SGD, lr inicial 0.005, coseno | 960 | 20 | 38.467% | 29.504% |
| yolo26s_sgd_box9_640_150e | SGD, lr inicial 0.005, coseno | 640 | 11 | 37.952% | 29.026% |

Se verificaron los 150 registros por corrida, mejores épocas por máximo de mAP50-95 val, existencia y hash SHA-256 de `best.pt` y `last.pt`, y hash de cada `results.csv`, contra `training_verified` en los registros de las campañas. Todos coincidieron.

`best.pt` se elige por validación durante entrenamiento; completar 150 épocas no significa que la época 150 sea mejor. La caída de validación y los cambios de pérdidas reportados son compatibles con sobreajuste. Las métricas de prueba publicadas corresponden a `best.pt`; no hay evaluación adicional de test de `last.pt` documentada.

Fuentes:

- `C:/Users/iceve/Documents/github/deteccion de agave/benchmark/agave_maleza_150ep_2026-10-21/status.json`
- `C:/Users/iceve/Documents/github/deteccion de agave/benchmark/agave_maleza_150ep_opciones34_2026-10-22/status.json`
- `C:/Users/iceve/Documents/github/deteccion de agave/docs/ENTRENAMIENTO_150_EPOCAS.md`
- `C:/Users/iceve/Documents/github/deteccion de agave/docs/ENTRENAMIENTO_OPCIONES_3_4_150_EPOCAS.md`
- `C:/Users/iceve/Documents/github/deteccion de agave/runs/detect/agave_maleza_150ep_2026-10-21/` (cada subcarpeta contiene `args.yaml`, `results.csv`, `results.png`, `weights/best.pt`, `weights/last.pt`).
- `C:/Users/iceve/Documents/github/deteccion de agave/runs/detect/agave_maleza_150ep_opciones34_2026-10-22/`.

## 5. Resultados comparables del conjunto combinado

Protocolo principal común: las mismas 136 imágenes/1115 cajas, tamaño de evaluación 640, batch 8, `conf=0.001`, `iou=0.7`, `max_det=300`, `half=false`, `augment=false`, `rect=true`, semilla 26. Este `conf` de evaluación para curvas no equivale necesariamente al umbral operativo para un video o actuador.

| Configuración | Precisión test | Recall test | mAP50 test | mAP50-95 test | mAP50-95 val reevaluado a 640 |
|---|---:|---:|---:|---:|---:|
| YOLO26s SGD 640, box=7.5 | 68.2014% | 62.5164% | 66.5478% | 24.3246% | 38.3269% |
| YOLO26s SGD 640, box=9.0 | 70.0661% | 62.0628% | 68.3423% | 24.2681% | 37.9420% |
| YOLO26n AdamW 640 | 67.6255% | 51.7061% | 58.6083% | 22.2284% | 37.6882% |
| YOLO26s SGD entrenado a 960 | 64.9066% | 52.4664% | 57.6924% | 20.9359% | 35.4547% |

Los valores reevaluados de val son distintos de los registrados durante entrenamiento y no deben sustituirse unos por otros sin explicar su origen.

La referencia para uso posterior es YOLO26s SGD 640, box=7.5: mayor mAP50-95 y recall en la comparación a 640. `box=9.0` aumenta precisión y mAP50, pero no mejora mAP50-95 ni recall. La comparación n/s cambia además optimizador y calendario, de modo que no aísla el efecto de tamaño de arquitectura. Las comparaciones SGD 640 frente a SGD 960 o box9 sí fueron diseñadas como variaciones de un parámetro nominal, con el matiz de que cambiar resolución también cambia la resolución de selección del checkpoint.

Fuentes numéricas primarias:

- `C:/Users/iceve/Documents/github/deteccion de agave/benchmark/agave_maleza_150ep_2026-10-21/agave_benchmark.csv`
- `C:/Users/iceve/Documents/github/deteccion de agave/benchmark/agave_maleza_150ep_opciones34_2026-10-22/agave_benchmark.csv`
- `C:/Users/iceve/Documents/github/deteccion de agave/docs/COMPARACION_CUATRO_MODELOS_150_EPOCAS_2026-10-22.md`

Peso de referencia verificado:

`C:/Users/iceve/Documents/github/deteccion de agave/runs/detect/agave_maleza_150ep_2026-10-21/yolo26s_sgd_640_150e/weights/best.pt`

SHA-256: `aef8bce09a9c76ae5ec0f30e2ef2f2958d681715e563fe9b4927399d827f28e7`.

## 6. Resolución cruzada: tabla separada

| Entrenamiento/selección | Evaluación | Precisión test | Recall test | mAP50 test | mAP50-95 test |
|---:|---:|---:|---:|---:|---:|
| 640 | 640 | 68.2014% | 62.5164% | 66.5478% | 24.3246% |
| 640 | 960 | 64.0845% | 62.0628% | 65.5320% | 22.3598% |
| 960 | 640 | 64.9066% | 52.4664% | 57.6924% | 20.9359% |
| 960 | 960 | 67.8888% | 60.6278% | 66.9835% | 24.6748% |

960/960 da el mayor mAP50-95 observado, apenas 0.3501 puntos porcentuales por encima de 640/640, con menor recall. Una corrida por configuración/una semilla y una prueba interna no permiten afirmar una superioridad estadística. No hay protocolo dedicado de velocidad de despliegue en estas campañas. Los checkpoints se fijaron por val, pero el ranking descriptivo y la recomendación usan observación de test; para nuevas decisiones iterativas conviene conservar una prueba externa no utilizada en selección.

Fuentes:

- `C:/Users/iceve/Documents/github/deteccion de agave/benchmark/agave_maleza_150ep_opciones34_2026-10-22/cross_resolution_benchmark.csv`
- `C:/Users/iceve/Documents/github/deteccion de agave/benchmark/agave_maleza_150ep_opciones34_2026-10-22/cross_resolution_protocol.json`

## 7. Resultado histórico: conservar como etapa, no como comparación controlada

El benchmark histórico incluye once corridas. Mejor corrida observada: `yolo26s_sgd_cos_slow_120e`, configurada para 120 épocas, detenida tras 86, mejor época 56. Test histórico (36 imágenes/403 cajas): precisión 69.3%, recall 61.5%, mAP50 65.4%, mAP50-95 21.3%. Estos valores están redondeados en el CSV histórico.

No calcular «mejora por agregar maleza» comparando directamente ese 21.3% con 24.32% del nuevo test: cambian las imágenes evaluadas, entrenamiento, política de parada y aumentos. Sería necesaria una evaluación común y un diseño que separe los efectos. El histórico es un antecedente experimental documentado.

Fuente: `C:/Users/iceve/Documents/github/deteccion de agave/benchmark/agave_benchmark.csv`.

## 8. Implicaciones para el escrito

Para el capítulo teórico procede desarrollar detección de objetos de una clase, CNN/YOLO26, aprendizaje por transferencia, cajas e IoU, precisión/recall/AP/mAP, aumentos, sobreajuste, independencia de particiones, seguimiento temporal y vínculo entre percepción y protección. Los números de datos, configuraciones y resultados anteriores corresponden a metodología y resultados, no a sustituir la fundamentación bibliográfica.

La redacción fiel al estado actual puede afirmar: «Se desarrolló y evaluó un módulo de detección de agaves a partir de imágenes RGB, ampliado con escenas que contienen maleza, como base perceptiva para un deshierbador autónomo». Debe mantener como pendientes o por verificar la caracterización seca/húmeda, validación externa, localización en unidades físicas, desempeño embebido, zona protectora efectiva y pruebas de ausencia de daño. Un recall global de 62.52% no es una tasa de protección ni una garantía de no corte.

No se revisaron secretos ni archivos de credenciales. La auditoría no ejecutó los comandos de entrenamiento sugeridos en los documentos.
