# Propuesta de explicación de YOLO para el capítulo 2

Texto de apoyo para revisar las secciones 2.3–2.5. No modifica el capítulo principal. Se comprobó la configuración oficial de Ultralytics **v8.4.57**.

## Texto propuesto

Para detectar un agave, el sistema recibe una imagen y produce una caja que indica dónde se encuentra la planta. YOLO permite realizar este proceso mediante una red neuronal que calcula la ubicación y la clase de los objetos en una misma evaluación. El nombre proviene de *You Only Look Once*. La propuesta original de Redmon et al. reunió estas tareas dentro de un modelo, y las versiones posteriores han modificado su estructura y entrenamiento [A].

Antes de procesar la imagen, se ajusta su tamaño. En Ultralytics, el procedimiento llamado *letterbox* puede conservar la proporción entre ancho y alto y completar el espacio restante con bordes. Por ejemplo, una fotografía de 2880 × 1620 píxeles puede reducirse a 640 × 360 y recibir relleno hasta formar una entrada cuadrada de 640 × 640. Esto evita deformar las plantas para hacerlas caber en el cuadrado. La forma final depende de la configuración: cuando se utiliza relleno rectangular mínimo, indicar tamaño 640 no implica necesariamente una entrada cuadrada [B, C].

La entrada conserva tres canales de color: rojo, verde y azul. En el preprocesamiento habitual de imágenes, sus valores se convierten a números entre cero y uno. Dentro de la red, estos datos pasan por operaciones sucesivas que producen nuevas representaciones de la escena. Para explicar este recorrido se suelen distinguir tres funciones: extracción de características, combinación de características y predicción de detecciones [B, D].

La extracción de características, conocida como *backbone* o bloque principal, aplica filtros cuyos valores se ajustan durante el entrenamiento. Sus respuestas permiten representar patrones locales, como cambios de intensidad y orientaciones de bordes. Al combinar capas, se obtiene información más compleja sobre la forma y la distribución de esos patrones. En un agave pueden resultar útiles los bordes alargados de las hojas y su disposición alrededor de la planta. Este ejemplo ayuda a interpretar la tarea, aunque no significa que cada filtro tenga asignado un nombre como «hoja» o «agave», ni que se haya comprobado qué patrón representa cada uno [E].

El bloque de combinación, denominado *neck* o cuello, reúne características procedentes de distintas etapas. En YOLO26 se utilizan mapas con diferentes resoluciones. Para una entrada cuadrada de 640 × 640, la cabeza de detección recibe mapas de 80 × 80, 40 × 40 y 20 × 20 posiciones, correspondientes a reducciones de 8, 16 y 32. Cada posición contiene varios valores calculados por la red; estos mapas no son tres fotografías reducidas. La información de mayor detalle espacial se combina con representaciones obtenidas en etapas más profundas [D, F].

Esta combinación es útil cuando los agaves tienen tamaños diferentes dentro de una escena. Una planta cercana puede ocupar gran parte de la imagen, mientras otra situada al fondo aparece pequeña y con menos detalle. Las distintas escalas aportan información para ambos casos, aunque no garantizan que todas las plantas sean detectadas. Tampoco deben confundirse estos mapas internos con entrenar el modelo a 640 o a 960 píxeles: cambiar la entrada modifica el detalle disponible desde el comienzo [D].

La cabeza de detección, o *head*, transforma las características en predicciones de cajas y puntuaciones de clase. En este proyecto la única clase es **agave**. Cada resultado incluye coordenadas y una puntuación de confianza, que se utiliza para seleccionar las detecciones conservadas. Una puntuación alta no garantiza que la caja sea correcta ni expresa una probabilidad de protección física. Las coordenadas se ajustan al tamaño de la imagen original para mostrar y utilizar el resultado [F, G].

YOLO26n y YOLO26s son variantes de distinta capacidad. En la configuración utilizada comparten el factor de profundidad, pero cambia el factor de anchura, que controla el número de canales internos. La variante *small* realiza más operaciones que la *nano*; su mayor capacidad no asegura mejores resultados en todos los datos. Su utilidad en Raspberry Pi debe establecerse midiendo tanto las detecciones como el tiempo de procesamiento [D].

## Referencias y precisiones para la edición

[A] Redmon et al., [artículo original de YOLO](https://arxiv.org/html/1506.02640v5). Su cuadrícula 7 × 7 pertenece a YOLOv1; no trasladarla a YOLO26.

[B] Ultralytics v8.4.57, [preprocesamiento de inferencia](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/engine/predictor.py).

[C] Ultralytics v8.4.57, [implementación LetterBox](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/data/augment.py).

[D] Ultralytics v8.4.57, [configuración YOLO26](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/cfg/models/26/yolo26.yaml). El YAML reúne fusión y detección bajo `head`; «cuello» es aquí una distinción funcional. El ejemplo 80/40/20 supone entrada cuadrada.

[E] LeCun, Bengio y Hinton, [Deep learning](https://doi.org/10.1038/nature14539), 2015.

[F] Ultralytics v8.4.57, [cabeza Detect](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/nn/modules/head.py). No atribuirle automáticamente la fórmula de confianza de YOLOv1.

[G] Ultralytics v8.4.57, [construcción de resultados y ajuste de coordenadas](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/models/yolo/detect/predict.py).

## Cinco pautas para acercar la voz al capítulo 1

1. Abrir cada tema con su función en el proyecto y después introducir el nombre técnico.
2. Usar ejemplos de hojas, sombras y plantas lejanas; explicarlos como ejemplos, no como hallazgos internos de la red.
3. Preferir «la red calcula» o «el programa registra» a frases abstractas como «constituye una base perceptiva».
4. Conservar una limitación cuando sea necesaria; evitar cerrar cada párrafo con una advertencia similar.
5. Mantener oraciones de extensión moderada y términos consistentes, corrigiendo los errores del capítulo 1 sin imitar su sintaxis defectuosa.
