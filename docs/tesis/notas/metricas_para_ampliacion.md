# Métricas y pérdidas: nota técnica para ampliar el capítulo 2

Revisión: 27 de octubre de 2026. Se leyó el código instalado de **Ultralytics 8.4.57** en el entorno del proyecto y se contrastaron siete archivos con su versión oficial etiquetada. Todos coincidieron después de normalizar los saltos de línea. Se revisaron el CSV de entrenamiento y la curva F1 de la corrida de referencia. No se entrenó, evaluó de nuevo ni modificó el capítulo.

Raíz local del paquete: `C:/Users/iceve/Documents/github/deteccion de agave/.venv/Lib/site-packages/ultralytics/`.

## 1. La evaluación empieza por definir qué cuenta como acierto

En detección no basta con afirmar que una imagen contiene agave. Hay que decidir qué predicción corresponde a cada planta anotada y si la caja está suficientemente cerca. Para ello se compara la clase y el solapamiento entre la caja predicha y la caja de referencia.

La intersección sobre unión, **IoU**, es el área compartida por las dos cajas dividida entre el área que cubren juntas:

`IoU = área de intersección / (área de caja predicha + área de referencia − área de intersección)`.

Una IoU de 0 significa que no se tocan; 1 significa coincidencia completa. No es una distancia en centímetros ni una probabilidad. En el ejemplo didáctico propuesto, `800 / (1200 + 1000 − 800) = 0.5714`. Esa caja puede cumplir un criterio IoU ≥ 0.50 y fallar uno IoU ≥ 0.75.

Para calcular AP, el validador usa diez umbrales: 0.50, 0.55, 0.60, …, 0.95. Exige clase coincidente y `IoU >= umbral`; resuelve las coincidencias evitando asignar una detección o una referencia más de una vez. Una predicción duplicada que queda sin referencia es falso positivo. Una planta sin predicción válida es falso negativo. Una caja mal localizada puede producir ambos: una predicción no emparejada y una referencia sin detectar.

Código: `models/yolo/detect/val.py:59` y `:298`; `engine/validator.py:286`. Fuentes oficiales: [validador de detección v8.4.57](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/models/yolo/detect/val.py#L59) y [emparejamiento de predicciones](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/engine/validator.py#L286).

## 2. Precisión, recall y F1: significado y cifras del software

**Precisión** responde: «De las detecciones aceptadas, ¿qué proporción fue correcta?». **Recall**, también llamado sensibilidad o exhaustividad, responde: «De los agaves anotados, ¿qué proporción se encontró?». El denominador cambia:

- `P = TP / (TP + FP)`.
- `R = TP / (TP + FN)`.
- `F1 = 2PR / (P + R)`.

Con veinte agaves anotados, quince encontrados correctamente y tres falsas detecciones: TP=15, FP=3, FN=5; precisión=83.33%, recall=75.00%, F1=78.95%. Son valores de un ejemplo inventado para explicar las fórmulas, no resultados del proyecto. F1 es una media armónica: disminuye cuando una de las dos medidas es baja. No expresa directamente el costo de dañar una planta.

**Detalle comprobado del software:** las columnas `metrics/precision(B)` y `metrics/recall(B)` no se calculan necesariamente a confianza 0.30. `ap_per_class` ordena las predicciones por confianza y construye curvas interpoladas en 1000 puntos. Para P/R usa los aciertos de la primera columna de IoU, es decir, IoU=0.50. Luego elige el índice que maximiza la curva F1 media entre clases, suavizada con factor 0.1, y toma P y R de sus curvas en ese índice. En este proyecto hay una sola clase, por lo que el promedio entre clases corresponde a agave.

El benchmark permite inicialmente predicciones con `conf=0.001` para construir las curvas; tampoco significa que P/R publicadas estén calculadas exactamente a 0.001. En la curva guardada de la referencia, la leyenda muestra F1≈0.65 en confianza≈0.168. Esta observación confirma que el resumen del test no corresponde al umbral 0.30 de los videos. No se debe tomar ese umbral obtenido del test como una nueva selección operativa: la elección de un umbral para uso posterior debe hacerse sobre validación y comprobarse por separado.

Código: `utils/metrics.py:788`, `:837`, `:854`, `:858`, `:877`. Fuente: [cálculo de métricas por clase](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/utils/metrics.py#L788). Evidencia visual local: `C:/Users/iceve/Documents/github/deteccion de agave/runs/detect/agave_maleza_150ep_2026-10-21/yolo26s_sgd_640_150e/evaluation/test/BoxF1_curve.png`.

Redacción accesible recomendada: «Al cambiar el nivel de confianza exigido, también cambia qué detecciones se aceptan. Por ello, precisión y recall deben interpretarse junto con el criterio utilizado para obtenerlas. Los valores resumidos por Ultralytics corresponden al punto seleccionado a partir de la curva F1; no representan automáticamente el funcionamiento del video a confianza 0.30».

## 3. AP y mAP: resumir una curva, no una confianza aislada

Al recorrer las predicciones desde mayor a menor confianza, se va admitiendo un número creciente de candidatos. Con cada incorporación cambian precisión y recall. **AP** resume el área bajo la relación precisión–recall a un criterio de IoU dado; no es el área bajo precisión frente a confianza, ni el promedio aritmético de precisión y recall.

En la implementación instalada, `compute_ap` añade extremos a las curvas, construye una envolvente de precisión no creciente, interpola en 101 valores de recall entre 0 y 1 y aplica integración trapezoidal. Es la definición numérica concreta de estos resultados. No debe afirmarse, solo por usar 101 puntos, que se ejecutó toda la evaluación oficial COCO con sus categorías por tamaño, límites y demás opciones.

**mAP50** promedia AP entre clases cuando IoU=0.50. **mAP50-95** promedia AP entre clases y los diez umbrales IoU de 0.50 a 0.95. Como aquí hay una clase, no se están promediando agave y maleza: mAP50 coincide con AP50 de agave y mAP50-95 agrega los diez niveles de exigencia espacial de esa clase. No significa «porcentaje de agaves que no serán cortados» ni «porcentaje de píxeles correctamente segmentados».

Una diferencia amplia entre mAP50 y mAP50-95 indica que el rendimiento disminuye al exigir cajas más ajustadas. Es compatible con dificultad de localización; no basta para medir error físico de la herramienta.

Código: `utils/metrics.py:756`, `:959`, `:977`. Fuente: [integración AP y agregación de métricas](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/utils/metrics.py#L756).

## 4. Matriz de confusión y significado del fondo

La matriz de detección de una clase tiene filas de **predicción** y columnas de **referencia**. La fila/columna adicional `background` permite contabilizar predicciones sin pareja y objetos no encontrados; **no es una clase maleza aprendida**.

| Predicción / referencia | Agave anotado | Sin referencia emparejada (fondo) |
|---|---|---|
| Agave detectado | Verdaderos positivos | Falsos positivos |
| Sin detección emparejada (fondo) | Falsos negativos | No representa verdaderos negativos contados |

En detección de objetos no se enumera cada posible región de fondo que el modelo dejó correctamente sin caja. Por eso la celda fondo–fondo no equivale a los TN de un clasificador binario y no permite obtener una exactitud global o especificidad bien definida con `TN/(TN+FP)`.

La versión normalizada divide **cada columna por su suma**, no la matriz por el total de objetos ni cada fila por su suma. La columna agave muestra cómo se distribuyen los agaves anotados entre detección y omisión. En un detector de una clase, la columna fondo puede mostrar 1.00 en la fila agave cuando hay falsos positivos; eso no significa que el sistema clasifique incorrectamente todo el fondo de la imagen.

Otro detalle esencial: la evaluación principal pasa `conf=0.001` al generador de la matriz, pero `ConfusionMatrix.process_batch` lo sustituye por **0.25**. Usa por defecto **IoU > 0.45** para sus emparejamientos. Así, esta matriz no tiene exactamente el mismo criterio que P/R al máximo F1 con IoU=0.50 ni que el video a confianza 0.30. No deben reconstruirse las cifras del benchmark a partir de ella suponiendo igualdad de umbrales.

Código local: `utils/metrics.py:397`, `:421`, `:444`, `:547`, `:589`; llamada en `models/yolo/detect/val.py:196`. Fuente: [matriz de confusión v8.4.57](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/utils/metrics.py#L397).

## 5. Confianza, IoU, NMS y asociación temporal son decisiones distintas

| Concepto | Pregunta que responde | Aplicación en el proyecto |
|---|---|---|
| Confianza | ¿El puntaje de esta detección supera el corte elegido? | 0.30 en las demostraciones de video; 0.001 como filtro inicial del benchmark |
| IoU de evaluación | ¿Se solapa lo suficiente con una caja anotada para contar como acierto? | 0.50–0.95 para AP; 0.45 por defecto en la matriz |
| IoU de NMS | ¿Dos predicciones de la misma imagen se solapan tanto que conviene suprimir una? | Argumento `iou`; solo actúa cuando la ruta ejecuta NMS |
| Asociación del tracker | ¿La detección actual puede corresponder al objeto observado antes? | BoT-SORT emplea costos/umbrales propios y estado temporal |

La confianza es un puntaje del modelo: un 0.80 no demuestra por sí mismo una probabilidad calibrada de 80% de acierto. IoU compara geometría; no mide esa confianza. NMS reduce duplicados dentro de una imagen y no mantiene identidades entre fotogramas.

En el YOLO26 `.pt` utilizado en octubre, la ruta end-to-end devuelve predicciones finales y omite la supresión NMS tradicional; el código de `non_max_suppression` retorna tras filtrar confianza y cantidad máxima. Por eso el cambio de argumento `iou` de 0.40 a 0.70 no debe presentarse como una mejora de NMS en esa ruta. Esto no elimina el uso de IoU para evaluar ni para asociar trayectorias. El export NCNN documentado tiene end-to-end desactivado y se debe describir por separado.

BoT-SORT del proyecto usa `match_thresh=0.8`, `fuse_score=True` y `with_reid=False`. Ese 0.8 es un umbral de asignación sobre costos; no equivale sin más a IoU mínima 0.8 ni al parámetro `iou` de inferencia. No hay reconocimiento por apariencia/ReID activo en esa configuración.

Fuentes: [rama end-to-end y NMS](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/utils/nms.py#L59), [BoT-SORT](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/trackers/bot_sort.py#L210), [asignación del tracker](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/trackers/byte_tracker.py#L326). Archivo local: `C:/Users/iceve/Documents/github/deteccion de agave/configs/tracking/botsort_agave.yaml`.

## 6. Función de pérdida: qué aprende el modelo y qué registra cada columna

Una **pérdida** es una señal numérica que orienta los ajustes de los pesos durante el aprendizaje. Una **métrica** resume el desempeño con un criterio de evaluación. Reducir una pérdida de entrenamiento es útil, pero no equivale automáticamente a mejorar mAP, detectar más plantas nuevas o protegerlas físicamente. Las pérdidas pueden tener ponderaciones y escalas distintas; sus valores no son porcentajes de error.

### box_loss

Penaliza la diferencia geométrica entre las cajas predichas y las cajas objetivo asignadas. El código usa **CIoU**: considera el solapamiento y además la separación de centros y la relación de aspecto. La contribución se pondera por los puntajes objetivo de la asignación y por el hiperparámetro `box`.

Explicación accesible: «Esta pérdida ayuda al modelo a colocar y ajustar el rectángulo alrededor del agave. Dos cajas pueden tocar la misma planta y, aun así, diferir en tamaño o posición; el entrenamiento penaliza esa diferencia». Una pérdida más baja no puede traducirse a centímetros sin calibración.

Como `box=9.0` pesa más esa contribución que `box=7.5`, no es correcto comparar sus valores brutos y afirmar que la corrida con cifra mayor localiza peor. Se comparan métricas y errores bajo el mismo protocolo.

### cls_loss

Es la contribución de clasificación. Se calcula mediante entropía cruzada binaria sobre logits y puntajes objetivo del asignador; los objetivos pueden ser suaves, no solamente etiquetas 0/1. Ayuda a que el modelo asigne puntajes adecuados a las predicciones relacionadas con el agave y reduzca respuestas incorrectas.

Que exista una sola clase no elimina este aprendizaje: el sistema debe aprender cuándo una predicción corresponde al agave. La existencia de `cls_loss` tampoco demuestra que haya una segunda clase maleza. Su valor se pondera con `cls`, y puede incluir ponderación de clases si esta opción está activa.

### dfl_loss: nombre heredado, contribución L1 en este YOLO26

**No debe explicarse esta columna como Distribution Focal Loss discreta activa.** El YAML oficial de YOLO26 declara `reg_max=1`, y se corroboró ese valor en la estructura serializada del checkpoint de referencia mediante inspección de su archivo pickle, sin ejecutarlo. En ese caso la cabeza no usa el módulo DFL discreto.

Sin embargo, el código **sí calcula una pérdida de regresión adicional**. Cuando `reg_max=1`, `BboxLoss` toma las distancias izquierda, arriba, derecha y abajo desde los puntos de referencia hasta los lados de la caja, las normaliza por el tamaño de imagen y penaliza diferencias absolutas mediante **L1**. La implementación devuelve esta contribución usando el nombre histórico `loss_dfl`, la multiplica por el hiperparámetro `dfl` y la guarda en la columna `dfl_loss`.

Redacción accesible sugerida: «Aunque el registro conserva el nombre `dfl_loss`, en la versión de YOLO26 usada aquí esa columna corresponde a una penalización L1 de las distancias que definen los bordes de las cajas. Su función es apoyar el ajuste geométrico de las predicciones. El nombre de la columna procede de la implementación y no significa que el modelo utilice la formulación discreta DFL de versiones anteriores».

Este hallazgo explica valores no nulos del CSV sin contradicción con la arquitectura libre de DFL. Conviene mantener `dfl_loss` al referirse a la figura original y aclarar su significado la primera vez, en lugar de cambiar silenciosamente el nombre del eje.

Fuentes verificadas: [configuración YOLO26 v8.4.57](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/cfg/models/26/yolo26.yaml#L8), [CIoU y rama L1 en BboxLoss](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/utils/loss.py#L110), [clasificación y ponderación de pérdidas](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/utils/loss.py#L431), [nombres de columnas](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/models/yolo/detect/train.py#L188).

Nota técnica opcional para metodología, no indispensable en la introducción didáctica: `E2ELoss` combina objetivos de las ramas one-to-many y one-to-one, con pesos que cambian durante entrenamiento; devuelve para el registro los componentes de la rama one-to-one. Por tanto, sumar las tres curvas registradas no reproduce automáticamente todo el objetivo de optimización de ambas ramas. Se confirmó en `utils/loss.py:1169` y el registro en `engine/trainer.py:454`. Fuente: [E2ELoss](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/utils/loss.py#L1169).

## 7. Curvas reales como respaldo de interpretación

En la referencia `yolo26s_sgd_640_150e`, el CSV contiene:

| Época | train box | train cls | train dfl/L1 | val box | val cls | val dfl/L1 | mAP50-95 val |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2.10690 | 3.77543 | 0.01387 | 1.91969 | 1.79651 | 0.01864 | 21.511% |
| 23 | 1.92468 | 1.16337 | 0.01254 | 1.83326 | 0.90539 | 0.01747 | 38.245% |
| 150 | 1.13772 | 0.46379 | 0.00669 | 2.09585 | 1.11590 | 0.02023 | 31.957% |

Esto permite explicar que el modelo puede seguir ajustándose mejor al entrenamiento mientras empeora en validación. Las tres observaciones son una ilustración; la conclusión de sobreajuste se apoya en las curvas completas, no en que una pérdida aislada suba una sola vez.

La función `fitness` de detección en esta versión asigna peso 1 a mAP50-95 y 0 a P/R/mAP50. Es coherente con seleccionar el checkpoint por mAP50-95 de validación. El máximo registrado está en época 23. No sustituir su 38.245% por el 38.3269% de la reevaluación posterior de `best.pt`: son registros distintos.

CSV leído: `C:/Users/iceve/Documents/github/deteccion de agave/runs/detect/agave_maleza_150ep_2026-10-21/yolo26s_sgd_640_150e/results.csv`.

Fuente del criterio de selección: [fitness de detección](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/utils/metrics.py#L1001).

## 8. Límites de esta nota

La descripción se refiere a la implementación fijada en 8.4.57 y a los archivos observados, no a toda versión de YOLO o Ultralytics. La documentación web de referencia actual sigue la rama principal y puede cambiar: para el escrito conviene citar el código etiquetado y registrar la versión. No se extrajeron P/R nuevas a confianza 0.30, no se cambió el umbral operativo y no se ejecutó inferencia adicional.

Las métricas de detección, el conteo por ID y la protección mecánica corresponden a niveles distintos. Aun una caja considerada TP a IoU=0.50 puede no representar todo el contorno de las hojas ni un margen suficiente respecto de la herramienta. Esa conexión exige calibración y validación propias.
