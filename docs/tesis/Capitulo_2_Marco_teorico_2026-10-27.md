# Capítulo 2. Marco teórico

La detección de agaves para apoyar el deshierbe autónomo requiere relacionar el reconocimiento visual de las plantas con las condiciones de operación de un sistema mecánico. Este capítulo presenta los fundamentos de la percepción mediante imágenes RGB, las redes neuronales convolucionales, la detección de objetos y su evaluación. También aborda el seguimiento temporal, la ejecución en una plataforma embebida y la información necesaria para definir regiones de protección alrededor del cultivo. Estos conceptos permiten interpretar el desarrollo experimental sin confundir la detección de una planta con la comprobación de que el mecanismo puede evitar dañarla.

## 2.1 Deshierbe selectivo y protección del cultivo

El deshierbe selectivo utiliza información sobre la ubicación de las plantas para decidir dónde debe actuar una herramienta. Xiang et al. distinguen dos estrategias de percepción: reconocer la maleza para intervenir sobre ella, o reconocer el cultivo para que el mecanismo lo evite [1]. La segunda estrategia fundamenta el enfoque de esta investigación, cuya clase de interés es el agave.

En este planteamiento, la detección proporciona una referencia espacial para delimitar regiones que deben preservarse. La maleza sigue siendo el objetivo de la labor agrícola, pero no necesita constituir una clase explícita del detector para estudiar la localización del cultivo. Esta elección concentra el aprendizaje en las características visuales del agave y permite analizar su reconocimiento frente a distintos fondos.

La ausencia de una detección no demuestra que una región contenga únicamente maleza. También puede corresponder a suelo, residuos o un agave que el modelo no reconoció. Por ello, en el sistema propuesto, la salida del detector debe interpretarse como información perceptiva sujeta a error. La habilitación del mecanismo requiere además conocer el área de trabajo y las condiciones bajo las cuales esa información es suficientemente reciente y confiable.

## 2.2 Imágenes RGB y variabilidad del entorno

Una imagen RGB representa la escena mediante tres canales de intensidad asociados al rojo, verde y azul. A partir de ellos pueden analizarse patrones de color, bordes, textura y distribución espacial. Sin embargo, una misma planta puede cambiar de apariencia por la iluminación, las sombras, la distancia a la cámara y la vegetación que la rodea. Qu y Su identifican la variabilidad ambiental y la complejidad del fondo como dificultades relevantes para el reconocimiento de cultivos y malezas [2].

Para este proyecto, la maleza seca y la maleza húmeda se consideran condiciones del escenario de observación. La distinción se refiere a la vegetación circundante, no al estado del agave. Su inclusión busca representar situaciones de campo en las que el contraste y la visibilidad de la planta pueden ser diferentes. La oclusión ocurre cuando parte del agave queda cubierta por otros elementos, de modo que la imagen conserva solo una parte de su estructura visible.

El color por sí solo no permite establecer el contenido de humedad de la maleza: una apariencia verde tampoco equivale necesariamente a una medición de humedad. En consecuencia, una evaluación por condición requiere registrar un criterio de clasificación durante la adquisición o revisión de los datos. Incluir imágenes con maleza amplía los escenarios disponibles, pero demostrar un desempeño comparable entre condiciones secas y húmedas exige identificarlas y evaluarlas por separado.

## 2.3 Redes neuronales convolucionales y aprendizaje por transferencia

Las redes neuronales profundas aprenden representaciones a partir de ejemplos. En visión por computadora, las redes convolucionales aplican filtros sobre regiones locales de una imagen y comparten sus parámetros entre posiciones. La combinación de estas operaciones con funciones no lineales permite construir representaciones sucesivas, desde patrones locales hasta características útiles para reconocer objetos [3].

El aprendizaje supervisado relaciona las imágenes de entrada con anotaciones que describen la respuesta esperada. En la detección de agaves, cada anotación indica la clase y la ubicación de una planta mediante una caja delimitadora. Durante el entrenamiento se ajustan los parámetros de la red para reducir diferencias entre sus predicciones y las anotaciones. La red aprende a partir de la información disponible; por ello, la consistencia del etiquetado es parte del fundamento experimental y no únicamente una tarea de preparación.

El aprendizaje por transferencia utiliza parámetros obtenidos previamente en otra tarea o conjunto de datos como punto de partida. Yosinski et al. estudiaron cómo varía la transferibilidad de las características aprendidas según la profundidad de la red y la relación entre tareas [4]. Este antecedente sustenta adaptar modelos preentrenados al reconocimiento de agaves, en lugar de suponer que todas sus características deben aprenderse desde una inicialización aleatoria.

El preentrenamiento no acredita por sí mismo el desempeño en campo. Las imágenes del proyecto deben representar la perspectiva de la cámara y las situaciones en las que se espera utilizar el detector. El ajuste sobre ellas y su evaluación posterior permiten determinar hasta qué punto las representaciones previas resultan útiles para la tarea específica.

## 2.4 Detección de objetos y representación de una sola clase

La clasificación asigna una categoría a una imagen o región; la detección identifica objetos y estima su ubicación, mientras que la segmentación describe regiones a nivel de píxel. La formulación de YOLO combina la predicción de cajas y categorías dentro de una red de detección [5]. En esta tesis se utiliza la detección mediante cajas, porque el desarrollo actual necesita localizar los agaves dentro de cada imagen.

Una detección puede expresarse como d = (x₁, y₁, x₂, y₂, c, s), donde las primeras cuatro componentes delimitan la caja, c corresponde a la clase y s es la puntuación de confianza. El centro geométrico se obtiene como xᶜ = (x₁ + x₂)/2 y yᶜ = (y₁ + y₂)/2. Estas coordenadas describen la imagen; no equivalen directamente a una posición en centímetros respecto a la herramienta.

El detector del proyecto considera una sola clase, denominada agave. La presencia de maleza en las imágenes no introduce automáticamente una segunda categoría. Las regiones que no se anotan como agave forman parte del contexto utilizado durante el aprendizaje. Por esta razón, las anotaciones deben incluir las plantas objetivo que sean identificables conforme a un criterio uniforme: omitirlas puede presentar al modelo información contradictoria.

Una caja también puede incluir suelo o vegetación ajena a la planta. Su centro no necesariamente coincide con el tallo y sus límites no representan con exactitud el contorno de cada hoja. Estas propiedades deben considerarse al utilizar las detecciones para proponer una región de protección.

## 2.5 Familia YOLO y modelo YOLO26

YOLO plantea la detección mediante una red que predice localizaciones y categorías a partir de la imagen completa [5]. Sus distintas versiones deben identificarse de manera explícita, porque comparten una familia de métodos, pero no necesariamente la misma arquitectura, función de pérdida o procedimiento de inferencia.

La documentación oficial de YOLO26 describe varias escalas de modelo, entre ellas nano y small, y una ruta de inferencia de extremo a extremo que puede producir detecciones sin una etapa separada de supresión de no máximos. También describe cambios en la regresión de cajas y en la receta de entrenamiento [6]. La supresión de no máximos, cuando se utiliza, filtra predicciones redundantes según su puntuación y solapamiento.

La configuración de la versión utilizada contiene un bloque de extracción de características, conexiones que combinan mapas de distintas escalas y una cabeza de detección. Esta última recibe tres mapas con reducciones espaciales de 8, 16 y 32 respecto a la entrada [6]. La combinación permite disponer de representaciones con distinto nivel de detalle. En la aplicación al agave, esta propiedad motiva estudiar plantas que ocupan diferentes tamaños dentro de la imagen debido a su distancia y a la perspectiva de la cámara.

Las variantes YOLO26n y YOLO26s forman parte de los experimentos de esta investigación. Su elección permite estudiar configuraciones de distinta capacidad y costo de procesamiento. No obstante, el nombre de una variante ligera no demuestra que cumpla los tiempos requeridos en una Raspberry Pi. Esa conclusión depende de la medición sobre el dispositivo, el tamaño de entrada y el formato de ejecución utilizados.

Asimismo, las características disponibles en la familia no deben atribuirse automáticamente a cada experimento. El optimizador efectivo, la ruta de inferencia y las opciones de exportación se establecen en la configuración registrada. Esta distinción es necesaria para describir con fidelidad los entrenamientos propios y su posterior despliegue.

## 2.6 Entrenamiento, particiones y generalización

El entrenamiento ajusta los parámetros mediante una función de pérdida. El descenso de gradiente estocástico, o SGD, calcula actualizaciones a partir de ejemplos o lotes de datos. La tasa de aprendizaje controla la magnitud de esas actualizaciones. Minimizar la pérdida de entrenamiento no equivale a garantizar un mejor desempeño sobre imágenes nuevas, porque el objetivo final es la generalización [7].

AdamW constituye otra alternativa de optimización y desacopla el decaimiento de pesos de la actualización adaptativa del gradiente [8]. El calendario de tasa de aprendizaje también influye en el proceso. Loshchilov y Hutter estudiaron un esquema de variación cosenoidal con reinicios [9]; utilizar una reducción cosenoidal en un experimento no significa que se hayan aplicado esos reinicios. Estos elementos deben distinguirse al comparar configuraciones.

Una época corresponde a un recorrido del conjunto de entrenamiento. Los parámetros guardados en una época forman un punto de control o checkpoint. El punto seleccionado por validación puede ser anterior al último guardado: completar un mayor número de épocas no convierte automáticamente al modelo final en el mejor. Cuando mejora el ajuste al entrenamiento y se deteriora la validación, el comportamiento es compatible con sobreajuste [7].

El conjunto de entrenamiento se utiliza para ajustar parámetros; el de validación, para orientar decisiones como la selección del checkpoint; y el de prueba, para estimar el desempeño de la configuración fijada. Kapoor y Narayanan muestran que la fuga de información puede generar conclusiones excesivamente optimistas sobre la capacidad de generalización [10]. En datos obtenidos de video, esta consideración resulta especialmente relevante: dos fotogramas próximos pueden mostrar casi las mismas plantas aunque sean archivos diferentes.

Para este proyecto, agrupar las imágenes por secuencia, recorrido o sesión de captura ofrece una unidad de separación más informativa que el archivo individual. Las transformaciones de aumento de datos deben aplicarse después de separar los conjuntos y conservar la coherencia de las anotaciones. Cambiar brillo, escala u orientación puede ampliar las variaciones de entrenamiento, pero no reemplaza la adquisición de condiciones de campo que no están representadas. Finalmente, modificar repetidamente el modelo después de observar el conjunto de prueba reduce su utilidad como evaluación independiente.

## 2.7 Métricas para evaluar la detección

La evaluación requiere comparar las cajas predichas con las anotaciones de referencia. La intersección sobre unión, conocida como IoU, expresa el área compartida entre dos cajas dividida entre el área de su unión. Un valor cercano a uno indica mayor coincidencia geométrica [11].

IoU(Bp, Br) = área de intersección / área de unión                                      (2.1)

Aquí, Bp es una caja predicha y Br una caja de referencia. Bajo un criterio de correspondencia definido, una detección correctamente asociada se cuenta como verdadero positivo (TP); una predicción sin correspondencia válida, como falso positivo (FP); y una anotación sin detección asociada, como falso negativo (FN). La precisión P y la sensibilidad o recall R se expresan como [12]:

P = TP / (TP + FP);                    R = TP / (TP + FN)                              (2.2)

La puntuación F1 combina ambas magnitudes mediante su media armónica [12]:

F1 = 2PR / (P + R)                                                                             (2.3)

La precisión media, AP, resume la relación precisión–recall al variar el umbral de confianza. La mAP promedia las AP entre clases. Con una sola clase, ese promedio no incorpora una categoría adicional de maleza. La notación mAP50 corresponde a IoU = 0.50; mAP50–95 considera diez umbrales, de 0.50 a 0.95 en incrementos de 0.05, siguiendo la convención utilizada en COCO [11]. Deben conservarse además los detalles del evaluador, porque compartir el nombre de una métrica no garantiza protocolos idénticos.

En la aplicación propuesta, un falso negativo representa un agave anotado que no fue reconocido conforme al criterio de evaluación. Esta omisión es relevante para la protección, aunque no permite calcular directamente una probabilidad de daño mecánico. Un falso positivo podría producir una inhibición innecesaria del mecanismo. Por ello, conviene interpretar precisión y recall de forma conjunta y examinar los errores de localización.

El umbral de confianza de una demostración en video debe distinguirse del utilizado para construir curvas de evaluación. Los valores agregados que entrega el evaluador no necesariamente describen el punto operativo elegido para el sistema [12]. Tampoco una diferencia pequeña entre dos resultados prueba superioridad estadística: la comparación requiere considerar la variación entre muestras, entrenamientos y condiciones de captura.

## 2.8 Seguimiento temporal y conteo por cruce de línea

La detección analiza la presencia y ubicación de objetos en cada imagen. El seguimiento busca asociar observaciones de diferentes instantes y mantener una identidad temporal. BoT-SORT combina información de movimiento, compensación del movimiento de la cámara y, en sus variantes correspondientes, información de apariencia para mejorar la asociación [13]. El uso de apariencia o reidentificación depende de la configuración concreta.

En los videos del proyecto, el seguimiento permite registrar eventos cuando el centro de una caja cruza una línea de referencia en una dirección definida. Contar una sola vez cada identificador evita repetir el evento para una misma trayectoria registrada, pero no garantiza que cada identificador represente una planta física distinta. Una planta puede perder su identidad y recibir otra; también puede ocurrir una asociación incorrecta entre plantas cercanas.

Por ello, el total de cruces es una salida del sistema y su exactitud necesita una referencia manual. La continuidad del seguimiento, los cambios de identidad y los intervalos sin observaciones deben evaluarse de forma diferenciada. Este módulo aporta información temporal útil para estudiar la secuencia de paso de las plantas, mientras que la protección requiere relacionar esa información con la posición y respuesta de la herramienta.

## 2.9 Inferencia en una plataforma embebida

Una plataforma embebida integra procesamiento en el equipo destinado a la tarea. En el desarrollo considerado, la Raspberry Pi permite estudiar la ejecución local del detector y la recepción de imágenes. El entrenamiento y la inferencia cumplen funciones distintas: el primero ajusta parámetros y la segunda utiliza los parámetros fijados para producir predicciones.

NCNN es un marco de inferencia desarrollado con énfasis en plataformas móviles y dispone de optimizaciones para arquitecturas ARM [14]. La exportación desde otro entorno permite utilizar un motor de ejecución diferente, pero requiere revisar las operaciones admitidas, el tamaño de entrada y el posprocesamiento [15]. Cambiar de formato tampoco equivale a reentrenar la red. La correspondencia entre predicciones debe comprobarse sobre imágenes comunes, especialmente si cambia la ruta de inferencia.

La tasa de adquisición, la tasa de presentación del video y la frecuencia del detector son magnitudes diferentes. Una interfaz puede actualizar imágenes mientras el detector procesa solo algunas de ellas. Para evaluar la utilidad temporal del sistema, interesa medir cuánto tiempo transcurre desde la adquisición de una observación hasta que su resultado queda disponible para una decisión.

En un esquema secuencial simplificado, el tiempo total incluye captura, espera, preprocesamiento, inferencia, posprocesamiento y comunicación. Si existen procesos concurrentes, conviene obtener la latencia mediante marcas temporales sobre cada observación, porque sumar promedios aislados puede describir incorrectamente el funcionamiento real. También deben registrarse la resolución de entrada, la alimentación y las condiciones térmicas. Una medición del modelo en imágenes almacenadas permite caracterizar una etapa, pero no sustituye la evaluación del sistema completo.

## 2.10 Relación entre detección y región de protección

La localización en píxeles debe relacionarse con la geometría del equipo antes de utilizarse para controlar una herramienta. La calibración de cámara permite estimar parámetros de formación de la imagen y corregir distorsiones. Zhang propuso un método de calibración mediante observaciones de un patrón plano desde distintas orientaciones [16]. Esta calibración constituye una base geométrica, pero por sí sola no establece toda la relación entre cámara, terreno, planta y herramienta.

En la propuesta de esta tesis, una región de protección debe considerar la extensión de la planta, la incertidumbre de localización y el movimiento ocurrido desde la adquisición de la imagen. Como relación cinemática simplificada, si el equipo avanza con velocidad constante v durante una latencia total T, recorre una distancia d:

d = vT                                                                                               (2.4)

Esta relación permite explicar por qué una detección correcta puede resultar insuficiente si llega tarde. Su uso supone que velocidad y tiempo se expresan en unidades compatibles; no determina por sí solo un margen de protección. La geometría de las hojas, el relieve, la vibración y la respuesta del mecanismo exigen una caracterización adicional.

La información perceptiva puede incluir la caja, su confianza, un identificador temporal y la marca de tiempo de la observación. A partir de ella puede estudiarse una lógica de inhibición dentro de la región que debe preservarse. La ausencia de detecciones no debe interpretarse como una autorización automática de corte. Este marco permite formular la integración posterior, mientras que comprobar la protección efectiva exige ensayos específicos del mecanismo y del cultivo, además de las métricas del detector.

# Referencias del capítulo

[1] M. Xiang et al., “Crop detection technologies, mechanical weeding executive parts and working performance of intelligent mechanical weeding: a review”, Frontiers in Plant Science, vol. 15, art. 1361002, 2024. [DOI: 10.3389/fpls.2024.1361002](https://doi.org/10.3389/fpls.2024.1361002).

[2] H.-R. Qu y W.-H. Su, “Deep Learning-Based Weed–Crop Recognition for Smart Agricultural Equipment: A Review”, Agronomy, vol. 14, núm. 2, art. 363, 2024. [DOI: 10.3390/agronomy14020363](https://doi.org/10.3390/agronomy14020363).

[3] Y. LeCun, Y. Bengio y G. Hinton, “Deep learning”, Nature, vol. 521, pp. 436–444, 2015. [DOI: 10.1038/nature14539](https://doi.org/10.1038/nature14539).

[4] J. Yosinski, J. Clune, Y. Bengio y H. Lipson, “How transferable are features in deep neural networks?”, Advances in Neural Information Processing Systems, vol. 27, pp. 3320–3328, 2014. [Actas originales](https://papers.nips.cc/paper_files/paper/2014/hash/532a2f85b6977104bc93f8580abbb330-Abstract.html).

[5] J. Redmon, S. Divvala, R. Girshick y A. Farhadi, “You Only Look Once: Unified, Real-Time Object Detection”, Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition, pp. 779–788, 2016. [Texto de los autores](https://arxiv.org/abs/1506.02640).

[6] Ultralytics, “Ultralytics YOLO26”, documentación oficial y configuración de arquitectura de la versión 8.4.57, consulta: 27 de octubre de 2026. [Modelos YOLO26](https://docs.ultralytics.com/models/yolo26/) y [configuración de la red](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/cfg/models/26/yolo26.yaml).

[7] I. Goodfellow, Y. Bengio y A. Courville, Deep Learning, MIT Press, 2016, cap. 8, “Optimization for Training Deep Models”. [Libro de los autores](https://www.deeplearningbook.org/contents/optimization.html).

[8] I. Loshchilov y F. Hutter, “Decoupled Weight Decay Regularization”, International Conference on Learning Representations, 2019. [Texto de los autores](https://arxiv.org/abs/1711.05101).

[9] I. Loshchilov y F. Hutter, “SGDR: Stochastic Gradient Descent with Warm Restarts”, International Conference on Learning Representations, 2017. [Texto de los autores](https://arxiv.org/abs/1608.03983).

[10] S. Kapoor y A. Narayanan, “Leakage and the reproducibility crisis in machine-learning-based science”, Patterns, vol. 4, núm. 9, art. 100804, 2023. [DOI: 10.1016/j.patter.2023.100804](https://doi.org/10.1016/j.patter.2023.100804).

[11] COCO Consortium, “COCO API: cocoeval.py”, implementación oficial de evaluación de detección, consulta: 27 de octubre de 2026. [Código del evaluador](https://github.com/cocodataset/cocoapi/blob/master/PythonAPI/pycocotools/cocoeval.py).

[12] Ultralytics, “utils.metrics”, código de evaluación, versión 8.4.57, 2026. [Código de la versión utilizada](https://github.com/ultralytics/ultralytics/blob/v8.4.57/ultralytics/utils/metrics.py).

[13] N. Aharon, R. Orfaig y B.-Z. Bobrovsky, “BoT-SORT: Robust Associations Multi-Pedestrian Tracking”, prepublicación arXiv:2206.14651, 2022. [Texto de los autores](https://arxiv.org/abs/2206.14651).

[14] H. Ni y The ncnn contributors, “ncnn”, 2017, repositorio oficial alojado por Tencent, consulta: 27 de octubre de 2026. [Repositorio del proyecto](https://github.com/Tencent/ncnn).

[15] Ultralytics, “Ultralytics YOLO NCNN Export”, documentación oficial, consulta: 27 de octubre de 2026. [Documentación de exportación](https://docs.ultralytics.com/integrations/ncnn/).

[16] Z. Zhang, “A Flexible New Technique for Camera Calibration”, IEEE Transactions on Pattern Analysis and Machine Intelligence, vol. 22, núm. 11, pp. 1330–1334, 2000. [DOI: 10.1109/34.888718](https://doi.org/10.1109/34.888718).
