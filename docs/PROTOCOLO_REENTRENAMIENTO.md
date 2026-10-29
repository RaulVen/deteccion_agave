# Protocolo del benchmark con imágenes nuevas

Preparado el 21 de octubre de 2026. El ejecutor queda listo para uso explícito; crear estos archivos, listar configuraciones o ejecutar `--check` no inicia entrenamiento ni evaluación.

## Estado de la comprobación del entorno

Durante una comprobación inicial, Windows rechazó la carga de `matplotlib.ft2font` con el mensaje «Una directiva de Control de aplicaciones bloqueó este archivo». Se observó un evento de Control de aplicaciones y los binarios locales coincidieron con los hashes del paquete. No se reinstalaron paquetes ni se modificaron políticas de seguridad.

Después de ampliar `--check` para importar realmente YOLO y las extensiones nativas, comprobaciones posteriores del ejecutor terminaron correctamente, incluyendo una con YOLO importado antes que NumPy/OpenCV/Matplotlib. Esto registra el estado observado; no demuestra una reparación permanente del bloqueo ni un entrenamiento completo. No se inició ninguna corrida. Repetir `--check` antes de iniciar y conservar el error original si Windows vuelve a bloquear una importación. La evidencia adicional se registra en `docs/verificacion_preparacion_2026-10-21.json`.

## Datos y comparación

- Dataset integrado: `datasets/prepared/agave_maleza_2026-10-21/data.yaml`.
- Dataset histórico: `datasets/yolo26/`; se conserva para reproducir y consultar los resultados anteriores.
- Configuraciones históricas: `configs/training/historico_2026-05_06/`. La prueba rápida original también se conserva en `runs/detect/runs/detect/agave_quick_test/args.yaml`.
- Configuraciones de esta repetición: `configs/training/agave_maleza_2026-10-21/`, una por cada una de las once corridas.
- Pesos iniciales: `models/pretrained/yolo26n.pt` y `models/pretrained/yolo26s.pt`.

Esta es una repetición del protocolo sobre un dataset distinto. Mantener los hiperparámetros no garantiza las mismas épocas ejecutadas ni métricas: cambian los datos y el punto de parada temprana. Todas las corridas usan los mismos splits nuevos. No cambiar etiquetas, particiones ni imágenes durante una serie de experimentos.

El export histórico usado en el benchmark contiene 404 imágenes originales de 2880×1620, sin preprocesamiento ni aumentación de Roboflow, y 4371 cajas de la clase `agave`. Sus splits son 295/73/36. La versión Roboflow aumentada de 699 imágenes no produjo ese benchmark. El nuevo entrenamiento aplica `imgsz=640` y sus aumentaciones locales a las imágenes preparadas.

Conservar agrupadas las imágenes cercanas del mismo recorrido al definir los splits reduce el riesgo de que fotogramas casi iguales aparezcan a ambos lados de la evaluación. Las guardas temporales no garantizan independencia espacial cuando se vuelve a recorrer una zona. `--check` valida archivos, clases y etiquetas, pero no decide agrupaciones temporales ni detecta duplicados visuales. Esa comprobación corresponde a la preparación del dataset y su manifiesto.

## Entorno y comprobación sin entrenamiento

El wrapper PowerShell usa `.venv/Scripts/python.exe` del repositorio, independientemente del directorio de trabajo. Python resuelve las rutas a partir de la ubicación del propio script. El dataset YAML debe tener `path` absoluto y `train`, `val`, `test` apuntando a directorios de imágenes; cada imagen debe tener su `.txt`, vacío cuando sea un negativo verificado.

Versiones del entorno histórico: Python 3.12.9, Ultralytics 8.4.57, PyTorch 2.10.0+cu128 y torchvision 0.25.0+cu128. El ejecutor comprueba Ultralytics, PyTorch, torchvision, NumPy, OpenCV y Matplotlib contra `Pipfile.lock`, la versión Python definida en `Pipfile` y disponibilidad CUDA de `device=0`. Además importa realmente NumPy, OpenCV, la extensión nativa `matplotlib.ft2font` y `ultralytics.YOLO`: tener los paquetes instalados no basta si una DLL está bloqueada o no puede cargarse. Un fallo conserva el mensaje original del sistema y hace fallar la comprobación. No instala ni actualiza paquetes ni altera políticas de seguridad.

Desde la raíz del repositorio:

```powershell
.\scripts\train_benchmark.ps1 --list
.\scripts\train_benchmark.ps1 --check
```

Sin argumentos se muestra la lista. `--check` revisa las once configuraciones, existencia de pesos, salidas disponibles, clases, rutas, pares imagen/etiqueta, formato de detección y coordenadas normalizadas. Imprime los conteos por split y el entorno; no carga imágenes en un entrenamiento, no evalúa modelos y no crea carpetas de corrida.

## Ejecución explícita

Una sola prueba de tres épocas:

```powershell
.\scripts\train_benchmark.ps1 --run agave_quick_test
```

Una configuración concreta:

```powershell
.\scripts\train_benchmark.ps1 --run yolo26s_sgd_cos_slow_120e
```

Después de completar la prueba rápida, ejecutar las diez pendientes:

```powershell
.\scripts\train_benchmark.ps1 --remaining
```

`--remaining` omite únicamente corridas completas: exige el JSON final, una fila en el CSV nuevo, `best.pt` y ambas carpetas de evaluación. Además comprueba que los hashes del YAML del dataset y de la configuración coincidan. Si encuentra una corrida parcial o inconsistente, se detiene y conserva los archivos para revisión; no los borra ni reanuda.

Las once corridas, secuencialmente, comenzando por la prueba rápida:

```powershell
.\scripts\train_benchmark.ps1 --all
```

`--all` incluye la prueba rápida y requiere destinos nuevos. Si alguna corrida ya existe, usar `--remaining` para omitir las completas o `--run NOMBRE` para una pendiente concreta. No mezcla una corrida nueva con una carpeta parcial. Una repetición adicional requiere un identificador de campaña y carpetas nuevos.

## Parámetros conservados

Los diez experimentos mantienen `batch=8`, `imgsz=640`, `seed=26`, GPU 0, cuatro workers, `deterministic=true`, `pretrained=true`, AMP y los hiperparámetros originales de optimización, pérdidas, aumentación y parada temprana. La prueba rápida mantiene tres épocas, batch 4, seed 0 y sus aumentaciones originales.

| Corrida | Épocas máximas | Patience | Optimizador declarado | lr0 | lrf | Cosine LR |
|---|---:|---:|---|---:|---:|---|
| agave_quick_test | 3 | 100 | auto | 0.01 | 0.01 | No |
| yolo26n_medium_aug_30e | 30 | 15 | auto | 0.01 | 0.01 | No |
| yolo26n_field_aug_60e | 60 | 20 | auto | 0.01 | 0.01 | No |
| yolo26n_field_aug_90e | 90 | 25 | auto | 0.01 | 0.01 | No |
| yolo26s_field_aug_60e | 60 | 20 | auto | 0.01 | 0.01 | No |
| yolo26s_coslr_balanced_45e | 45 | 12 | AdamW | 0.002 | 0.05 | Sí |
| yolo26s_loss_box_dfl_45e | 45 | 12 | AdamW | 0.002 | 0.01 | No |
| yolo26s_loss_precision_45e | 45 | 12 | AdamW | 0.0015 | 0.01 | No |
| yolo26s_adamw_cos_low_lr_120e | 120 | 30 | AdamW | 0.001 | 0.02 | Sí |
| yolo26s_sgd_cos_slow_120e | 120 | 30 | SGD | 0.005 | 0.01 | Sí |
| yolo26s_adamw_box_focus_120e | 120 | 30 | AdamW | 0.0012 | 0.02 | Sí |

Los YAML nuevos contienen parámetros de entrenamiento y validación pertinentes, sin opciones de exportación, vídeo o visualización ajenas a esta ejecución. Las diferencias deliberadas son rutas nuevas, `exist_ok=false` y eliminación del `save_dir` histórico. `resume=false` se mantiene. Los nombres de modelo se resuelven a los pesos locales, sin depender de descargas implícitas.

Con `optimizer=auto`, Ultralytics 8.4.57 ignora el `lr0` y momentum escritos en YAML. Con el dataset histórico de una clase eligió AdamW, lr 0.002, momentum 0.9 y warmup_bias_lr 0. En esta versión la elección depende de clases y del número estimado de iteraciones; por encima de 10000 puede cambiar a MuSGD. El ejecutor conserva `auto` para repetir la regla histórica y registra la salida del optimizador. Fijar explícitamente el optimizador efectivo sería un experimento distinto y debe documentarse como tal.

`auto_augment` y `erasing` se conservan tal como aparecen en los argumentos históricos, pero pertenecen a aumentación de clasificación y no se deben presentar como aumentos aplicados a detección. Las configuraciones y el log son la referencia de cada corrida.

## Evaluación y CSV nuevo

Después de cada entrenamiento se carga su `weights/best.pt` y se evalúan por separado `val` y `test`, con el mismo protocolo para todos:

```text
imgsz=640, batch=8, device=0, workers=4
conf=0.001, iou=0.7, max_det=300
half=false, augment=false, rect=true
seed=26, deterministic=true, plots=true
```

`conf=0.001` es el umbral mínimo de candidatos para evaluar curvas; precisión/recall reportados por Ultralytics no equivalen a medir únicamente el punto operacional de tracking `conf=0.30`. `iou=0.7` es el parámetro de posprocesamiento; las métricas mAP50 y mAP50-95 usan sus correspondientes IoU de evaluación. Se conserva el modo end-to-end del checkpoint YOLO26; algunos parámetros NMS no alteran esa ruta.

No se recuperó el comando exacto de evaluación de test del benchmark antiguo. Este protocolo queda explícito para las corridas nuevas; los valores antiguos se conservan y no se anuncian como una comparación controlada sobre el mismo test.

El CSV nuevo usa las mismas columnas del histórico: corrida, modelo, épocas registradas, mejor época, precisión, recall, mAP50 y mAP50-95 de val/test, y ruta al peso. La mejor época se obtiene del máximo mAP50-95 de validación en `results.csv`. El orden de presentación es mAP50-95 de test descendente y mAP50 para desempate. Para elegir hiperparámetros usar validación; consultar test repetidamente durante la selección deja de representar un conjunto reservado.

## Comparación opcional con los pesos anteriores

Para comparar los modelos históricos contra los splits nuevos sin entrenarlos:

```powershell
.\scripts\train_benchmark.ps1 --baseline yolo26s_sgd_cos_slow_120e
.\scripts\train_benchmark.ps1 --baseline all
```

El ejecutor lee las rutas de `benchmark/agave_benchmark.csv`, comprueba que las clases del checkpoint coincidan con el dataset nuevo y aplica exactamente el protocolo de evaluación anterior. Guarda los resultados en otro CSV. Los splits de evaluación conservan las 73 imágenes de validación y las 36 de test históricos y añaden imágenes de la nueva salida; no contienen las 295 imágenes históricas de entrenamiento. Los conjuntos históricos ya se consultaron durante el estudio previo, por lo que la comparación debe interpretarse con esa limitación y con la correlación temporal documentada.

## Salidas y conservación

- Entrenamientos: `runs/detect/agave_maleza_2026-10-21/<corrida>/`.
- Evaluaciones de modelos nuevos: `<corrida>/evaluation/val` y `test`.
- Evaluaciones históricas: `runs/detect/agave_maleza_2026-10-21/baseline/<corrida>/val` y `test`.
- Benchmark nuevo: `benchmark/agave_maleza_2026-10-21/agave_benchmark.csv`.
- Comparación de pesos históricos: `benchmark/agave_maleza_2026-10-21/historical_models_on_new_dataset.csv`.
- Argumentos, entorno, métricas y hashes: `benchmark/agave_maleza_2026-10-21/metadata/`.
- Logs: `benchmark/agave_maleza_2026-10-21/logs/`.

No se sobrescriben los YAML, pesos, CSV ni corridas históricas. Cada corrida exige que su destino no exista. Los checkpoints se guardan por Ultralytics y los resultados CSV se incorporan sólo después de terminar las dos evaluaciones. Ante un fallo se conserva el log y la carpeta parcial para revisión; no se borran ni reanudan automáticamente.

Un archivo `.runner.lock` evita dos ejecutores simultáneos. Una salida normal o error controlado lo retira. Después de un cierre forzado, comprobar que no exista otro proceso del ejecutor antes de retirar manualmente un lock antiguo. Los argumentos completos quedan impresos en el log incluso si no se alcanza la escritura final del JSON de métricas.
