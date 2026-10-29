# Auditoría de aumento de datos para ampliar el capítulo 2

Fecha: 27 de octubre de 2026. Trabajo de lectura de configuraciones, registros y código; no se ejecutó entrenamiento ni se modificaron datos. Esta nota aporta insumos y ejemplos, no sustituye la redacción del capítulo.

## 1. Hallazgo principal

Las cuatro corridas nuevas guardaron exactamente los mismos parámetros de aumento de datos. La diferencia entre YOLO26n y YOLO26s no incluye una receta distinta de estos aumentos, pese a que el nombre de la corrida nano contiene `campo`. Las diferencias de modelo, optimizador, resolución o peso de pérdida deben explicarse por separado.

Activos en la ruta de detección de Ultralytics 8.4.57: variaciones HSV, escala, cizallamiento, perspectiva, reflexión horizontal y MixUp. Desactivados por valor cero: rotación, traslación aleatoria, reflexión vertical, Mosaic, CutMix y Copy-Paste. `auto_augment=randaugment` y `erasing=0.15` aparecen en la configuración general, pero solo se consumen por la ruta de clasificación; no son aumentos activos de estas corridas de detección.

`augment:false` tampoco significa «entrenamiento sin aumentos». En la configuración general corresponde a aumento durante predicción (TTA). El conjunto de entrenamiento se construye con `augment=mode == "train"`, independientemente de ese campo general.

## 2. Configuraciones auditadas

Base: `C:/Users/iceve/Documents/github/deteccion de agave/`.

1. `runs/detect/agave_maleza_150ep_2026-10-21/yolo26s_sgd_640_150e/args.yaml`.
2. `runs/detect/agave_maleza_150ep_2026-10-21/yolo26n_campo_640_150e/args.yaml`.
3. `runs/detect/agave_maleza_150ep_opciones34_2026-10-22/yolo26s_sgd_960_150e/args.yaml`.
4. `runs/detect/agave_maleza_150ep_opciones34_2026-10-22/yolo26s_sgd_box9_640_150e/args.yaml`.

Todas declaran `task:detect`, `rect:false` durante entrenamiento, 150 épocas, `close_mosaic:0`, `multi_scale:0.0`, semilla 26 y los valores siguientes. Los logs de las cuatro corridas confirman Ultralytics 8.4.57. El código local leído en `.venv/Lib/site-packages/ultralytics/__init__.py` declara la misma versión.

## 3. Tabla exacta y significado

| Parámetro | Valor en las cuatro corridas | Naturaleza del valor | Efecto real en detección |
|---|---:|---|---|
| `hsv_h` | 0.02 | Amplitud del cambio de tono, no probabilidad | Activo. Desplazamiento aleatorio aditivo entre −3.6 y +3.6 unidades del tono OpenCV de ciclo 180, aproximadamente ±7.2 grados del círculo cromático; se aplica con retorno circular. |
| `hsv_s` | 0.55 | Amplitud de ganancia, no probabilidad | Activo. Multiplicador aleatorio de saturación entre 0.45 y 1.55, con recorte al rango del canal. |
| `hsv_v` | 0.35 | Amplitud de ganancia, no probabilidad | Activo. Multiplicador aleatorio del valor/brillo entre 0.65 y 1.35, con recorte. |
| `degrees` | 0 | Amplitud angular en grados | Rotación aleatoria desactivada. No se introdujo un giro de ±grados mediante este parámetro. |
| `translate` | 0.0 | Amplitud de desplazamiento respecto al tamaño de salida | No se añade desplazamiento aleatorio por esta opción. El centrado, escala y perspectiva todavía pueden cambiar coordenadas; no equivale a «ninguna caja se desplaza». |
| `scale` | 0.35 | Amplitud de escala, no probabilidad | Activo. Factor uniforme entre 0.65 y 1.35 respecto a la imagen preparada. Puede reducir o ampliar plantas y recortar lo que salga del lienzo. |
| `shear` | 2 | Amplitud de cizallamiento en grados | Activo en ambos ejes; se muestrean ángulos entre −2° y +2° y se usan sus tangentes en la matriz. Inclina/deforma geometría, no es lo mismo que rotar. |
| `perspective` | 0.0005 | Amplitud de dos coeficientes proyectivos | Activo. Coeficientes uniformes entre −0.0005 y +0.0005. No son grados ni probabilidad de 0.05%; el cambio visual depende también de coordenadas y resolución. |
| `fliplr` | 0.5 | Probabilidad de reflexión horizontal | Activo: 50% de probabilidad por aplicación; no exige que exactamente la mitad de las imágenes guardadas se refleje. |
| `flipud` | 0.0 | Probabilidad de reflexión vertical | Desactivado. El histórico tenía 0.5 en configuraciones comparables; las nuevas corridas ya no invierten arriba y abajo. |
| `mosaic` | 0.0 | Probabilidad de aplicar Mosaic | Desactivado durante toda la corrida. No se entrenó con composiciones Mosaic a partir de cuatro escenas. |
| `mixup` | 0.05 | Probabilidad de aplicar MixUp | Activo: 5% de probabilidad por aplicación. El coeficiente de mezcla se toma de Beta(32,32), usualmente próximo a una mezcla mitad y mitad. **0.05 no significa 5% de opacidad.** Se combinan anotaciones de las dos imágenes. |
| `cutmix` | 0.0 | Probabilidad de aplicar CutMix | Desactivado. No atribuir recortes pegados de otra imagen a este experimento. |
| `copy_paste` | 0.0 | Control de selección/aplicación de instancias, según modo | Desactivado. Además, la implementación requiere segmentos; estos datos de detección tienen cajas, no máscaras. En el modo guardado `flip`, seleccionaría una fracción de instancias elegibles, no simplemente una probabilidad global por imagen. |
| `auto_augment` | `randaugment` | Nombre de política automática | Inerte en estas corridas: opción de clasificación, no invocada por `v8_transforms` para detección. |
| `erasing` | 0.15 | Probabilidad de borrado aleatorio en clasificación | Inerte en detección. **No afirmar que se ocultó aleatoriamente el 15% de imágenes o plantas.** |
| `close_mosaic` | 0 | Número de épocas finales para cerrar mezclas | No se programa un cierre anticipado de mezclas. Con `mosaic=0`, Mosaic está inactivo desde el principio; MixUp sigue siendo elegible hasta el final. |

Otros campos relevantes: `bgr=0.0` no añade intercambio aleatorio de canales; `multi_scale=0.0` no activa entrenamiento multiescala de tamaño de lote. Esto no desactiva `scale=0.35`: son mecanismos distintos. El entrenamiento a 960 utiliza la misma amplitud de aumentos que el de 640, pero actúa sobre otro tamaño de procesamiento.

## 4. Explicaciones sencillas y ejemplos aplicables al agave

**Aumento de datos:** se produce una versión transformada de una imagen de entrenamiento para mostrar variaciones al modelo. Por ejemplo, una misma escena puede aparecer algo más oscura o con las plantas a otra escala. Las transformaciones se generan al leer muestras durante el entrenamiento; no implican que se hayan capturado nuevas plantas ni que el dataset archivado crezca por esa cantidad.

**Variaciones de color:** cambiar brillo puede presentar un agave y su entorno más claros u oscuros; cambiar saturación reduce o intensifica los colores; variar tono desplaza ligeramente el color. Se busca disminuir la dependencia de una apariencia específica. No reproduce fielmente toda sombra real, exposición, reflejo ni condición climática. Tampoco convierte de forma físicamente válida maleza seca en húmeda: el estado de humedad debe documentarse con escenas reales y un criterio explícito.

**Escala:** el mismo agave puede verse más pequeño o más grande dentro de la entrada. Ayuda a exponer distintas apariencias de tamaño, pero no reproduce toda la información de otra distancia real ni recupera detalles que no estaban presentes. `scale=0.35` significa factores de 0.65 a 1.35, no que el aumento se aplique al 35% de casos.

**Reflexión horizontal:** una planta que estaba a la izquierda aparece a la derecha como en un espejo, y se transforman sus cajas. Puede representar la variación visual lateral de las filas. No reproduce un cambio real de recorrido, ni debe utilizarse para explicar el movimiento temporal de la máquina. Se desactivó la reflexión vertical en las nuevas corridas, de modo que el aumento no invierte deliberadamente suelo y parte superior de la escena.

**Cizallamiento y perspectiva:** se alteran las relaciones geométricas de la escena para presentar deformaciones controladas. Pueden aproximar parte de las variaciones visuales por orientación de cámara. Una transformación proyectiva de la imagen no equivale a capturar todas las caras 3D de la planta ni a simular exactamente una cámara montada con cualquier inclinación. Las hojas que antes no eran visibles no aparecen con información real nueva.

**MixUp:** dos escenas se superponen con transparencia y se conservan los objetos anotados de ambas. Es una regularización sintética, no una fotografía físicamente real de doble vegetación. La intención es dificultar la memorización de fondos y favorecer aprendizaje a partir de señales distribuidas; no se ha aislado aquí su contribución al rendimiento. El 5% es la probabilidad de mezclar, mientras que la transparencia se decide mediante otro valor aleatorio.

**Transformación de etiquetas:** si la imagen cambia geométricamente, la caja del agave debe cambiar con ella. Dejar las coordenadas anteriores enseñaría una localización equivocada. En esta implementación, la misma transformación se aplica a instancias; se recortan cajas al lienzo y se filtran casos geométricamente inadecuados. Un cambio de color no requiere mover las cajas.

**Regularización y límites:** observar variaciones puede contribuir a reducir memorización, pero no garantiza eliminar el sobreajuste. Las cuatro corridas mostraron deterioro de validación después de máximos tempranos pese a estos aumentos. No se hizo una comparación de la misma configuración con y sin cada transformación; por tanto, no se puede atribuir causalmente una mejora a HSV, MixUp o perspectiva.

## 5. Cuándo se aplican y por qué separar validación y prueba

La construcción del dataset usa `augment=mode == "train"` (`data/build.py:263`). En la ruta de detección, `YOLODataset.build_transforms` llama a `v8_transforms` solo si `self.augment` es verdadero (`data/dataset.py:218`). Si es falso, utiliza LetterBox con `scaleup=False` y el formateo de datos, sin estas variaciones aleatorias (`data/dataset.py:224`).

Por tanto, los aumentos de esta tabla forman parte de entrenamiento; no se aplican como aumentos aleatorios de entrenamiento a validación/prueba. Ambos conjuntos sí requieren preprocesamiento de tamaño y formato para entrar al modelo. Preprocesar no equivale a aumentar datos. La evaluación documentada tiene `augment=false`; no se utilizó TTA para combinar predicciones de diversas versiones de una imagen.

La separación de conjuntos debe ocurrir antes de generar derivados. Una versión aclarada o reflejada de una imagen de entrenamiento no sirve como prueba independiente de generalización de ese mismo objeto/escena. Aumentar datos tampoco corrige la proximidad temporal ya presente en los splits históricos.

## 6. Comprobación de rutas de código y opciones inertes

En `.venv/Lib/site-packages/ultralytics/data/augment.py`:

- `v8_transforms` comienza en línea 2692; usa `RandomPerspective` en 2723 y construye la secuencia final en 2753: pretransformación, MixUp, CutMix, Albumentations opcional, HSV, reflexión vertical y horizontal. No consulta `erasing` ni `auto_augment`.
- `RandomPerspective._compute_affine_matrix`, líneas 1100–1142, muestra los rangos y composición geométrica. `apply_instances`, línea 1183, transforma y filtra las cajas.
- `RandomHSV`, líneas 1463–1473, separa desplazamiento de tono y ganancias de saturación/valor.
- `RandomFlip.get_params`, línea 1519, aplica `random.random() < self.p`.
- `MixUp.get_params`, línea 808, utiliza Beta(32,32); línea 823 mezcla intensidades; línea 836 concatena instancias y clases.
- `CopyPaste.__call__`, línea 1883, abandona la transformación si no hay segmentos o si p=0. En modo `flip`, línea 1926 selecciona `round(p*n)` instancias elegibles.
- `classify_augmentations`, línea 2817, implementa las opciones de clasificación; `data/dataset.py:1006` y 1007 pasan allí `erasing` y `auto_augment`.
- `cfg/default.yaml:66` describe `augment` como TTA; líneas 127–128 identifican las dos opciones como clasificación.
- `engine/trainer.py:413` cierra mezclas cuando `epoch == epochs-close_mosaic`; con épocas 150 y `close_mosaic=0`, el entrenamiento ordinario recorre índices 0–149 y no llega al índice 150. No hay cierre anticipado.

**Albumentations opcional:** `v8_transforms` incluye un adaptador que, si está instalada la biblioteca, puede activar Blur, MedianBlur, ToGray y CLAHE con probabilidad 0.01 cada uno. En el entorno local revisado no existe un paquete/directorio Albumentations, no figura en `Pipfile.lock` y los logs de las cuatro corridas no muestran activación de esos transformadores. No hay evidencia suficiente para atribuirlos como técnicas realizadas; no añadirlos al listado experimental demostrado. La configuración no contiene transformaciones personalizadas.

## 7. Fuentes primarias citables

Para principios generales y ejemplos, [guía oficial de aumento de datos de Ultralytics](https://docs.ultralytics.com/guides/yolo-data-augmentation). Consultada el 27 de octubre de 2026. Es documentación evolutiva; la conducta exacta del experimento debe sustentarse con la versión siguiente.

- Ultralytics. *data/augment.py*, versión 8.4.57. [Código oficial de transformaciones](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/data/augment.py).
- Ultralytics. *data/dataset.py*, versión 8.4.57. [Construcción de transformaciones y ruta de clasificación](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/data/dataset.py).
- Ultralytics. *data/build.py*, versión 8.4.57. [Activación de aumentos solo en entrenamiento](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/data/build.py).
- Ultralytics. *cfg/default.yaml*, versión 8.4.57. [Definición de argumentos y ámbitos](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/cfg/default.yaml).

En el capítulo 2 conviene explicar los conceptos sin llenar la sección de nombres de argumentos. La tabla de valores exactos puede reservarse para metodología, conservando una conexión breve con las transformaciones efectivamente empleadas. Las referencias específicas de técnicas (por ejemplo, artículo original de MixUp) pueden complementar este soporte de implementación, pero no son necesarias para resolver qué hizo cada parámetro en estas corridas.

## 8. Frases que se deben evitar

- «Se generaron imágenes reales de maleza húmeda a partir de maleza seca».
- «El aumento de datos multiplicó el número de muestras independientes».
- «Se utilizó Random Erasing al 15%» o «RandAugment mejoró la detección», basándose únicamente en `args.yaml`.
- «MixUp combinó una imagen al 5% con otra al 95%».
- «El modelo no usó aumentos porque `augment:false`».
- «Los modelos usaron aumentos distintos porque uno se llama `campo`».
- «Se desactivaron todos los aumentos al final» por `close_mosaic:0`.
- «Los aumentos eliminaron el sobreajuste».
