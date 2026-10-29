# Detección de agave de temprana edad mediante redes neuronales profundas en condiciones de maleza seca y húmeda para apoyar el deshierbe selectivo

Raúl Eduardo Venegas Reyes

Universidad Autónoma de Zacatecas

Maestría en Ciencias y Tecnología de la Luz y la Materia

## Capítulo 1 Introducción

La incorporación de visión artificial a los implementos agrícolas permite relacionar las decisiones de manejo con la posición de las plantas. En el deshierbe selectivo, esta relación resulta especialmente importante: la herramienta debe intervenir en las zonas destinadas al control de maleza y conservar una separación respecto al cultivo. La agricultura de precisión proporciona el contexto para este tipo de decisiones localizadas, cuyo valor depende de transformar la información del entorno en acciones oportunas y verificables [1].

Esta investigación aborda la detección de agaves de temprana edad mediante imágenes RGB y redes neuronales profundas, como base para generar zonas de protección que orienten el funcionamiento de un sistema deshierbador. El interés se concentra en reconocer el cultivo cuando está rodeado por maleza seca o húmeda, con diferentes niveles de cobertura y oclusión. La condición de la maleza se considera una característica del escenario de evaluación; la clase objetivo del detector es el agave.

El principio de operación consiste en inhibir la intervención sobre las regiones ocupadas por el agave y habilitarla únicamente en las zonas de trabajo que satisfagan las condiciones geométricas y temporales definidas para el implemento. En consecuencia, la ausencia de una detección no constituye por sí sola una prueba de presencia de maleza ni garantiza que una región esté libre de agaves. El problema de investigación comprende tanto el reconocimiento visual como la transformación de sus resultados en información de protección del cultivo.

El trabajo parte de una base de datos y de experimentos preliminares con YOLO26s. A partir de estos avances, se propone ampliar la evaluación a las condiciones de maleza señaladas, analizar los errores de detección y medir el desempeño del procesamiento embebido. La contribución esperada es un procedimiento reproducible para determinar en qué condiciones el sistema puede aportar información útil al deshierbe selectivo, sin anticipar resultados de protección o eliminación de maleza que todavía requieren validación.

### 1.1 Antecedentes

El manejo de malezas forma parte de las labores de establecimiento y mantenimiento de los cultivos de agave. Como antecedente agronómico, Figueroa Castro estudió la identificación y el control de malezas asociadas a agaves alcoholígenos en Guerrero, considerando tanto la respuesta de la vegetación no deseada como el daño al cultivo [2]. Este antecedente muestra la necesidad de evaluar conjuntamente la intervención y la conservación de la planta productiva. Sus resultados pertenecen a especies, tratamientos y condiciones locales específicas, por lo que no se extrapolan de forma directa a la parcela de esta investigación.

La visión artificial permite obtener información espacial a partir de imágenes del campo. La revisión de Wang, Zhang y Wei organiza métodos de detección de maleza mediante visión terrestre y procesamiento de imágenes [3]. Qu y Su analizan posteriormente el reconocimiento de cultivo y maleza mediante aprendizaje profundo, y señalan la importancia de las condiciones ambientales, las etapas de crecimiento y las oclusiones en el desempeño del reconocimiento [4]. Estas aportaciones sustentan la necesidad de evaluar el sistema con imágenes que representen su entorno de operación.

Además del reconocimiento explícito de maleza, existe el enfoque de localizar el cultivo para evitarlo durante el trabajo mecánico. Melander, Lattanzi y Pannacci evaluaron sistemas de deshierbe intrahilera guiados por cámara en cebolla y col trasplantadas [5]. El antecedente es pertinente porque conecta la identificación de las plantas cultivadas con el movimiento de herramientas entre ellas. No demuestra que una configuración equivalente funcione en agave, pero sí fundamenta el principio de protección del cultivo que orienta esta tesis.

En agave, Espinoza-Hernández y colaboradores emplearon YOLOv4 y YOLOv4-tiny con imágenes aéreas RGB para estimar la densidad de plantas [6]. Su trabajo confirma la pertinencia de investigar detectores convolucionales en este cultivo. La presente investigación plantea un escenario diferente: una cámara terrestre asociada a un implemento, con cambios de perspectiva, posibles oclusiones por maleza y restricciones de tiempo para emitir una señal de protección.

El desarrollo local ya cuenta con imágenes de una parcela de Juchipila, Zacatecas, con agaves reportados de dos años al momento de la adquisición, de acuerdo con la presentación de avance de junio de 2026 [15]. También se dispone de un conjunto de 404 imágenes organizado para detectar una sola clase, agave, y de experimentos con YOLO26. Estos materiales constituyen el punto de partida del nuevo alcance. Su disponibilidad no acredita todavía que la base represente de manera equilibrada la maleza seca y húmeda; esa cobertura deberá documentarse durante la ampliación y revisión de los datos.

### 1.2 Estado del arte

La literatura revisada permite distinguir varias líneas que convergen en el problema de esta tesis. La primera estudia la visión terrestre para diferenciar elementos del campo mediante características visuales y métodos de aprendizaje. Los trabajos de revisión de Wang et al. [3] y Qu y Su [4] proporcionan un panorama de esta evolución y de las dificultades que aparecen al pasar de imágenes controladas a ambientes agrícolas variables. Para esta investigación, su aportación principal es justificar que la evaluación incluya diversidad de escenas y no únicamente imágenes favorables.

Una segunda línea integra reconocimiento visual y tratamiento localizado. Wang y colaboradores desarrollaron un sistema de aspersión dirigida para maleza en trigo durante el macollamiento [7]. El interés de este antecedente está en la relación entre detección y control, no en trasladar su actuación química al deshierbe mecánico. Las diferencias entre cultivos, herramientas y condiciones de captura impiden asumir que un rendimiento publicado será reproducible con el sistema de agave.

La tercera línea se relaciona con la localización necesaria para intervenir cerca de una planta. Lottes y colaboradores propusieron combinar clasificación cultivo-maleza con detección de tallos para tratamientos específicos [8]. Su investigación distingue la identificación visual de la estimación de posiciones útiles para una herramienta. Esta distinción es central en agave: una caja que contiene parte de las hojas puede ser adecuada para registrar una detección, pero no necesariamente define por sí misma la región que debe evitar el implemento.

En el deshierbe mecánico guiado por cámara, el estudio de Melander et al. [5] aporta evidencia de sistemas que evitan las plantas cultivadas mientras trabajan dentro de la hilera. Las condiciones de cultivo y ajuste de la herramienta forman parte de su desempeño. Este antecedente permite plantear la detección de agave como información para la exclusión de zonas, sin requerir que la red identifique todas las especies de maleza presentes.

En cuanto al cultivo objetivo, Espinoza-Hernández et al. [6] evaluaron detección de agave en imágenes aéreas. El estudio reportó un F1 de 0.95 para YOLOv4 y de 0.96 para YOLOv4-tiny bajo sus condiciones experimentales. Tales cifras no son comparables directamente con las del proyecto actual: cambian la perspectiva, la resolución espacial, el conjunto de datos y el procedimiento de evaluación. El antecedente se utiliza para fundamentar la detección visual del agave, no como garantía de exactitud terrestre.

La familia YOLO plantea la detección mediante una red que predice localizaciones y clases a partir de una imagen [9]. El desarrollo más reciente utilizado en este proyecto es YOLO26s. Jocher y colaboradores describen YOLO26 como una familia de modelos con cambios en la arquitectura y el entrenamiento, entre ellos un diseño de doble cabeza y una opción de inferencia sin supresión de no máximos [10]. La documentación del desarrollador complementa esa descripción y debe consultarse junto con la versión concreta del programa utilizada [11].

La necesidad de investigación se sitúa en la adaptación y validación de este conjunto de ideas para agave de temprana edad: reconocimiento terrestre bajo maleza seca y húmeda, delimitación de regiones de protección y operación con recursos de cómputo limitados. La revisión presentada no pretende demostrar la inexistencia absoluta de trabajos similares; identifica las diferencias que los antecedentes consultados no resuelven para el sistema y la parcela estudiados.

### 1.3 Planteamiento del problema

El funcionamiento selectivo de un deshierbador requiere conocer dónde debe suspenderse la intervención para conservar el cultivo. En una plantación de agave, la presencia de maleza puede ocultar parcialmente las hojas y modificar el fondo contra el que se observa cada planta. La maleza seca y la húmeda representan condiciones que deben incorporarse al análisis, junto con la cantidad de vegetación, la iluminación y la perspectiva de captura.

Un detector puede omitir un agave o ubicarlo de forma imprecisa. Si sus resultados se convierten directamente en órdenes de actuación, una omisión puede dejar una planta sin protección, mientras que una detección falsa puede suspender el trabajo en una región que sí podría intervenirse. Por tanto, seleccionar el modelo únicamente por una métrica global no resuelve el problema operativo. Se requiere conocer la distribución de sus errores y la anticipación con que entrega la información.

#### 1.3.1 Descripción del problema

Los avances disponibles muestran que YOLO26s reconoce agaves en imágenes del proyecto. En el conjunto de prueba histórico se reportaron precisión de 0.693, sensibilidad o recall de 0.615, mAP50 de 0.654 y mAP50-95 de 0.213 [15]. Estas métricas describen una evaluación preliminar. No demuestran protección suficiente del cultivo, ni permiten concluir que el desempeño se mantenga cuando aumenta la oclusión o cambia la condición de la maleza.

La implementación embebida introduce otra restricción. Una prueba local en Raspberry Pi 4 de 2 GB registró un tiempo medio de 1.0657 s por llamada de predicción y un rendimiento aproximado de 0.94 imágenes por segundo, con entrada de inferencia configurada a 320 píxeles [16]. El ensayo excluyó captura RTSP, visualización y control del implemento. Por ello, todavía falta medir la latencia del sistema completo y relacionarla con la velocidad de desplazamiento y con la distancia disponible entre observación y actuación.

El problema queda definido como la falta de una evaluación integrada que determine si la detección de agave, bajo las condiciones de maleza seca y húmeda consideradas, proporciona localizaciones y tiempos de respuesta compatibles con una política de protección del cultivo. Resolverlo exige evaluar el reconocimiento y la generación de señales como partes de un mismo proceso, manteniendo identificadas sus limitaciones.

#### 1.3.2 Formulación del problema

¿En qué condiciones un sistema de visión basado en YOLO26, implementado en una plataforma embebida, puede detectar agaves de temprana edad rodeados por maleza seca o húmeda y generar oportunamente zonas de exclusión para apoyar un deshierbe selectivo que preserve el cultivo?

De esta pregunta se desprenden cuestiones específicas: ¿cómo cambia la sensibilidad del detector entre condiciones de maleza y grados de oclusión?, ¿qué compromiso existe entre omisiones, falsas detecciones y latencia?, y ¿qué margen de protección y anticipación necesita la salida lógica para evitar intervenciones sobre la región del agave en los escenarios evaluados?

### 1.4 Justificación

La justificación agronómica se encuentra en la necesidad de manejar la vegetación no deseada conservando las plantas de agave. El antecedente de Figueroa Castro [2] considera el daño al cultivo como variable distinta de la eficacia de control. Esta separación se retoma en el proyecto: reconocer un agave y evitarlo es un objetivo verificable del sistema de percepción, mientras que la eliminación efectiva de maleza corresponde a la respuesta del mecanismo y requiere una evaluación propia.

La justificación del cambio de enfoque parte de una decisión funcional. El objeto que debe preservarse es conocido y puede etiquetarse de manera consistente como una sola clase. Identificarlo permite formular regiones de exclusión sin construir inicialmente un catálogo de todas las malezas posibles. Los antecedentes de herramientas guiadas por reconocimiento del cultivo respaldan este principio [5]. Sin embargo, la reducción del número de clases no elimina la dificultad de reconocer agaves ocultos ni convierte el fondo en una clase de maleza confirmada.

La justificación tecnológica de una red profunda reside en estudiar si las representaciones aprendidas permiten reconocer el cultivo frente a variaciones del escenario. Las redes convolucionales emplean filtros compartidos para procesar información espacial, y sus parámetros se ajustan mediante entrenamiento [12]. Para esta tesis, el interés es evaluar esa capacidad con datos propios de agave y contrastarla con un método básico de referencia. La robustez ante maleza seca y húmeda se plantea como una propiedad por demostrar experimentalmente.

YOLO26s se adopta como modelo de referencia porque ya forma parte del desarrollo documentado y permite conservar la trazabilidad entre datos, pesos entrenados y pruebas de inferencia. La elección no implica que sea la arquitectura óptima para cualquier plataforma. Se deberá comparar su desempeño con una variante de menor costo computacional o con una configuración optimizada, conservando condiciones de evaluación equivalentes. El marco teórico desarrolla sus fundamentos y distingue las características de la familia YOLO26 de los parámetros efectivamente utilizados en el proyecto.

La justificación científica consiste en estudiar el desempeño por condición de captura y relacionar los errores del detector con una regla de protección. Un promedio obtenido al reunir todas las escenas puede ocultar una pérdida de sensibilidad en las más difíciles. Separar los resultados por humedad observada, cobertura y oclusión permitirá identificar el dominio en el que el sistema funciona y los escenarios que requieren más datos o una restricción de operación.

Finalmente, la ejecución local en una plataforma embebida permite investigar una integración que no dependa del envío continuo de imágenes a un servidor. Su conveniencia práctica deberá sustentarse con mediciones de latencia, recursos y estabilidad. La reducción de costos, del uso de herbicidas o del daño al cultivo se considera un beneficio potencial de una integración futura; no se presenta como resultado alcanzado por el detector.

### 1.5 Alcance del trabajo

El trabajo comprende la adquisición y organización de imágenes RGB, el entrenamiento y evaluación de un detector de agave de temprana edad, su ejecución en Raspberry Pi y el diseño de una salida lógica de protección y habilitación. La evaluación considerará maleza seca y húmeda, con distintos grados de cobertura y oclusión. El origen inicial de los datos corresponde a la parcela de Juchipila documentada en el avance de junio [15]; cualquier incorporación de nuevas parcelas, edades o fechas deberá registrarse.

La red tendrá como clase objetivo el agave. La condición seca o húmeda se documentará como metadato del escenario, sin convertirla necesariamente en una clase de detección. Tampoco se asumirá que la imagen RGB mide contenido de agua. La humedad deberá describirse mediante un procedimiento de observación en campo y, si se pretende una cuantificación física, mediante una medición independiente.

La salida del sistema señalará las regiones que deben protegerse y la posibilidad de habilitar una intervención dentro de una zona previamente autorizada para deshierbe. El diseño mecánico del implemento queda fuera del alcance principal. La comprobación inicial de la lógica podrá realizarse con video y señales de prueba; la eficacia agronómica, el daño real a las plantas y la sincronización física solo podrán afirmarse cuando se efectúen ensayos con el mecanismo correspondiente.

El conteo por cruce de línea y el seguimiento temporal se consideran herramientas auxiliares. Permiten examinar la continuidad de las detecciones y registrar eventos, pero no sustituyen la validación de protección del agave. Asimismo, la calibración de una línea en pantalla no equivale a una calibración métrica cámara-herramienta.

La generalización quedará limitada a los escenarios representados y evaluados. Los agaves completamente ocultos, las imágenes inutilizables y las condiciones que excedan el dominio de prueba requerirán una política de inhibición o supervisión. El trabajo no incluye identificación taxonómica de malezas, diagnóstico de humedad de la planta ni garantías de funcionamiento para cualquier terreno o velocidad.

### 1.6 Hipótesis

Un detector YOLO26 ajustado con imágenes representativas de agaves de temprana edad en escenarios con maleza seca y húmeda permitirá obtener mayor sensibilidad de detección, a una tasa comparable de falsas detecciones, que un método de referencia basado en color y geometría. Al incorporar un margen espacial de protección y compensación temporal, sus resultados permitirán generar señales de inhibición antes de que la región del cultivo alcance la zona de intervención, dentro de un intervalo de velocidades determinado experimentalmente.

La hipótesis contiene dos afirmaciones contrastables. La primera se comprobará con datos independientes y resultados separados por condición. La segunda se evaluará registrando si cada agave de referencia recibió protección oportuna y midiendo las habilitaciones que intersecten regiones del cultivo. Los márgenes admisibles y los umbrales de aceptación se fijarán antes de la prueba final, a partir de la geometría y la respuesta del implemento, para evitar ajustarlos retrospectivamente a los resultados.

### 1.7 Objetivo General

Desarrollar y evaluar un sistema de visión artificial basado en redes neuronales profundas para detectar agaves de temprana edad en imágenes RGB bajo condiciones de maleza seca y húmeda, implementarlo en una plataforma embebida y generar información espacial y temporal que permita inhibir la intervención sobre el cultivo y apoyar la habilitación selectiva de un sistema deshierbador.

### 1.8 Objetivos Particulares

1. Adquirir y organizar imágenes y videos RGB de agaves de temprana edad, registrando la condición seca o húmeda de la maleza, su cobertura, la oclusión del cultivo y las condiciones de captura.

2. Construir y depurar un conjunto de datos con anotaciones de agave, separando entrenamiento, validación y prueba por secuencias, recorridos o fechas para reducir la dependencia entre particiones.

3. Entrenar y comparar configuraciones de YOLO26 mediante precisión, sensibilidad y métricas de localización, con análisis de errores por escenario y comparación con un método básico de referencia.

4. Implementar el modelo seleccionado en Raspberry Pi y medir latencia, rendimiento, consumo de memoria y estabilidad durante el procesamiento del flujo de imágenes previsto.

5. Diseñar una lógica que transforme las detecciones en zonas de protección y señales de inhibición o habilitación, considerando margen espacial, antigüedad de la información y tiempo de respuesta.

6. Validar la oportunidad y coherencia de las señales mediante secuencias anotadas y pruebas controladas, identificando las condiciones de operación y las limitaciones para su integración al deshierbador.

### 1.9 Metodología

La investigación tendrá un enfoque experimental y aplicado. Se organizará en fases que permitan seguir la relación entre datos de campo, predicciones y decisiones de protección. Las mediciones históricas se conservarán como línea base; las nuevas pruebas se identificarán mediante versiones de datos, configuración y pesos del modelo.

#### 1.9.1 Definición de escenarios y adquisición

La adquisición buscará representar maleza seca y húmeda sin confundir la humedad con el estado de desarrollo de la vegetación. El registro de campo distinguirá la condición de humedad observada, la presencia de material verde o senescente y el nivel de cobertura. Una planta verde puede tener superficie seca, y un residuo senescente puede encontrarse mojado; por ello, estos atributos se documentarán por separado.

Se registrarán fecha, recorrido, posición y orientación de cámara, resolución, condiciones de iluminación y edad aproximada del cultivo. Se incluirán escenas con poca y abundante maleza, así como casos de oclusión parcial. La categoría de oclusión se determinará mediante una rúbrica visual reproducible y revisión de anotadores; no se presentará como porcentaje físico exacto si no existe una medición que lo sustente.

La comparación de humedad deberá evitar, en lo posible, que todas las escenas secas correspondan a una parcela o fecha y todas las húmedas a otra. Cuando no puedan equilibrarse esas variables, se reportará la asociación y se limitará la interpretación: una diferencia de desempeño entre grupos no demostraría por sí sola un efecto causal de la humedad.

#### 1.9.2 Anotación y organización del conjunto de datos

Las imágenes se anotarán con cajas de la clase agave mediante un criterio consistente sobre hojas visibles, plantas parcialmente ocultas y objetos en los bordes. Los casos ambiguos se revisarán antes de incorporarse al entrenamiento. Las escenas sin agave visible podrán incluirse como ejemplos negativos, después de comprobar que no contienen plantas reconocibles sin anotar.

La separación de datos se realizará por unidades de adquisición. Los fotogramas cercanos de un mismo recorrido no se distribuirán indiscriminadamente entre entrenamiento y prueba. Se revisarán además recorridos repetidos sobre las mismas plantas, pues una separación por archivo de video no garantiza independencia si el contenido es casi idéntico. Los aumentos derivados de una imagen permanecerán en su partición de entrenamiento.

El conjunto histórico contiene 295 imágenes de entrenamiento, 73 de validación y 36 de prueba [15]. Su uso anterior para comparar experimentos obliga a tratar sus métricas como exploratorias. La evaluación final del nuevo enfoque requerirá una prueba reservada que no intervenga en la selección de arquitectura, umbrales o aumentos.

#### 1.9.3 Entrenamiento y comparación

Se utilizará YOLO26s como referencia y se documentarán pesos iniciales, resolución, tamaño de lote, optimizador, tasa de aprendizaje, aumentos y criterio de parada. La corrida histórica denominada yolo26s_sgd_cos_slow_120e empleó SGD y una programación coseno de la tasa de aprendizaje; el nombre alude a 120 épocas configuradas, mientras que los registros disponibles contienen 86 épocas ejecutadas. Esta distinción deberá conservarse en la descripción experimental.

Se comparará el modelo con una variante más ligera o una alternativa de inferencia optimizada y con un método básico de color y geometría. El objetivo del método básico será establecer una referencia verificable, sin atribuirle de antemano un desempeño inferior. La selección utilizará validación y priorizará el compromiso entre sensibilidad de agave, falsas detecciones y latencia. La prueba final permanecerá separada de estas decisiones.

#### 1.9.4 Evaluación del reconocimiento

Se calcularán precisión, sensibilidad, F1, AP50 y AP50-95, indicando el criterio de correspondencia entre cajas y los umbrales empleados [13]. Para una sola clase, la media entre clases coincide con el AP de agave. Se conservará la denominación mAP cuando corresponda a la salida del programa, explicando esta particularidad.

El informe separará resultados para maleza seca y húmeda y mostrará el número de imágenes, plantas y secuencias de cada grupo. Se examinarán por separado oclusiones, objetos pequeños y localizaciones insuficientes. Cuando se calculen intervalos mediante remuestreo, se usarán secuencias o recorridos como unidades para evitar tratar fotogramas correlacionados como observaciones independientes.

#### 1.9.5 Implementación y medición temporal

La implementación recibirá imágenes de la cámara RGB, ejecutará el detector y conservará marcas de tiempo asociadas a la captura o recepción y a la salida. Se medirán por separado los tiempos accesibles de adquisición, procesamiento, comunicación y respuesta. Si solo se dispone de la hora de recepción del flujo, se declarará que la latencia previa de cámara y transmisión aún debe caracterizarse.

Se registrarán mediana, percentiles altos de latencia, imágenes procesadas por segundo, uso de memoria y comportamiento durante sesiones prolongadas. La prueba histórica de Raspberry Pi [16] servirá como referencia de ejecución aislada, no como sustituto de la medición con cámara y salida. Cada cambio de resolución o formato del modelo requerirá revisar también la calidad de detección.

#### 1.9.6 Generación de zonas de protección

Las detecciones se transformarán en regiones de exclusión ampliadas por un margen ajustado a la incertidumbre de localización y al implemento. La zona de intervención y las regiones del cultivo deberán expresarse en un sistema de coordenadas común. Mientras no exista calibración física, la evaluación se limitará a regiones de imagen y señales simuladas.

La lógica habilitará la intervención únicamente dentro del área de trabajo autorizada, cuando no exista intersección con una región protegida y la información mantenga vigencia temporal. La pérdida del flujo, una detección obsoleta o una condición fuera del dominio de operación producirán inhibición. La ausencia de cajas no será equivalente a una certificación automática de terreno libre de agaves: la evaluación deberá comprobar precisamente las omisiones que esta regla no puede detectar por sí sola.

El seguimiento podrá contribuir a mantener temporalmente la protección de una planta ya observada y registrar su paso por una referencia. Se verificará su configuración antes de atribuirle capacidades de asociación o reidentificación. El uso previo de BoT-SORT y el conteo de 41 eventos en un segmento constituyen una demostración operativa [15], no una medición de exactitud del conteo ni de protección.

#### 1.9.7 Validación de la salida y análisis

En video anotado se registrará cada oportunidad de paso de un agave por la zona de intervención. Se medirá la proporción de plantas con inhibición oportuna, las habilitaciones que intersecten una región de cultivo y el tiempo o área excluidos innecesariamente. El registro incluirá el margen espacial y la velocidad utilizados. Estas variables permiten identificar cuándo una mejora en protección implica una menor superficie disponible para deshierbe.

Una primera prueba utilizará señales de simulación o una salida de banco, seguida de ensayos controlados cuando se disponga de la integración mecánica. Solo estos últimos permitirán evaluar contacto, daño y eficacia real de deshierbe. La discusión final relacionará el desempeño visual con la oportunidad de las señales y establecerá límites de operación sustentados por las mediciones.

## Capítulo 2 Marco Teórico

### 2.1 Percepción del cultivo y deshierbe selectivo

La percepción agrícola obtiene descripciones del entorno que un sistema de decisión puede utilizar para orientar una labor. En este proyecto se distinguen tres elementos: el cultivo que debe preservarse, la región autorizada para trabajar y el estado de habilitación del implemento. La detección del cultivo informa sobre el primero; la geometría de operación establece el segundo, y la lógica de control determina el tercero.

El antecedente de deshierbe intrahilera guiado por cámara [5] respalda la posibilidad de reconocer plantas cultivadas para evitar su daño. En la formulación aquí propuesta, la red entrega evidencia espacial del agave y el controlador la convierte en una exclusión. El término selectivo se refiere a esa restricción de intervención. No implica que el modelo clasifique todas las regiones exteriores como maleza.

Esta distinción modifica el criterio de evaluación. Un falso negativo de agave puede dejar una región sin protección; un falso positivo puede aumentar el área excluida. Ambos errores afectan el funcionamiento, pero sus consecuencias son diferentes. La selección del umbral deberá considerar esa asimetría y medirse en relación con la salida del sistema.

### 2.2 Imágenes RGB y variabilidad del escenario

Una imagen RGB representa la escena mediante canales rojo, verde y azul. La apariencia registrada depende de la iluminación, la respuesta de la cámara y las superficies observadas. La revisión de Qu y Su destaca que el reconocimiento agrícola está condicionado por el ambiente, el crecimiento y las oclusiones [4]. En consecuencia, una representación útil en determinada adquisición puede perder eficacia en otra condición.

Para este estudio, maleza seca y húmeda son categorías de adquisición. No se presupone que toda diferencia entre ellas sea visible o que la red estime agua a partir del color. La humedad observada se registrará por separado del verdor, la senescencia y la cobertura. La finalidad es comprobar si el detector mantiene su respuesta ante los escenarios documentados, sin convertir una clasificación contextual en una medición fisiológica.

La oclusión reduce la información visible del agave. Su efecto debe distinguirse del cambio de fondo: una planta rodeada de abundante vegetación puede permanecer visible, mientras que una cantidad menor de maleza situada frente a ella puede ocultar una región relevante. Esta diferencia motiva registrar tanto cobertura del escenario como visibilidad del cultivo.

### 2.3 Redes neuronales convolucionales y aprendizaje supervisado

Una red neuronal profunda representa una función con parámetros ajustables que transforma entradas en salidas. En el aprendizaje supervisado, las imágenes se acompañan de anotaciones y el entrenamiento reduce una función de pérdida. Las redes convolucionales utilizan filtros compartidos sobre regiones de la imagen, lo que permite aprender patrones espaciales y combinarlos a través de distintas capas [12].

La transferencia de aprendizaje consiste en iniciar el ajuste a partir de parámetros aprendidos previamente. El aumento de datos introduce transformaciones de los ejemplos de entrenamiento, y la validación permite examinar la generalización durante el ajuste [12]. Ninguna de estas estrategias sustituye imágenes reales del dominio de aplicación.

En agave, la hipótesis práctica es que la red aprenda evidencia útil de la planta aun cuando varíe el entorno. No se debe afirmar, sin un análisis específico, que el modelo reconoce una estructura botánica concreta o que ignora por completo el fondo. Una alta respuesta en imágenes similares a las de entrenamiento puede reflejar dependencia de condiciones particulares; de ahí la necesidad de recorridos independientes y análisis por escenarios.

### 2.4 Clasificación detección y segmentación

La clasificación asigna una etiqueta a una imagen o región. La detección añade la localización de los objetos mediante cajas. La segmentación describe regiones a nivel de píxel; en su modalidad de instancias distingue objetos individuales. YOLO26 dispone de variantes para distintas tareas, pero el modelo utilizado en este proyecto corresponde a detección [11].

Una caja delimitadora aproxima la extensión de un agave en la imagen. Su interior puede contener suelo o maleza y su contorno puede omitir puntas de hojas. Por ello, la caja no equivale a la silueta exacta ni al volumen que ocuparía la planta frente a una herramienta. El margen de protección es una decisión geométrica adicional que debe validarse.

La detección resulta congruente con las anotaciones disponibles y con una primera integración por regiones. Si la evaluación demuestra que la localización mediante cajas es insuficiente, la segmentación o la detección de puntos relevantes podrían investigarse como extensiones. Esta posibilidad no autoriza a describir el detector actual como segmentador.

### 2.5 Fundamento de YOLO y actualización a YOLO26

Redmon y colaboradores formularon YOLO como una aproximación que obtiene cajas y probabilidades de clase a partir de la imagen completa mediante una sola red [9]. Esa organización proporciona una base para sistemas que necesitan localizar varios objetos por imagen. Las velocidades reportadas en el trabajo original corresponden a su arquitectura y equipo; no definen el rendimiento del sistema actual.

YOLO26 incorpora un diseño con dos cabezas de detección, una alternativa de inferencia sin NMS y una regresión de cajas que elimina Distribution Focal Loss. El trabajo de Jocher et al. también describe MuSGD, Progressive Loss y Small-Target-Aware Label Assignment como componentes de su propuesta de entrenamiento [10]. Se trata de características de la familia y su receta publicada, que deben distinguirse de la configuración elegida para un experimento particular.

En el proyecto, la corrida de referencia empleó SGD. Por tanto, sería incorrecto indicar que el entrenamiento realizado utilizó MuSGD únicamente por tratarse de YOLO26. Del mismo modo, la ruta de inferencia efectiva debe documentarse a partir de la versión instalada y sus argumentos; la documentación actual contempla rutas con y sin NMS [11]. La presencia de un parámetro IoU en un archivo no basta para demostrar qué ruta ejecutó una versión anterior.

La escala s identifica la variante seleccionada. Su justificación experimental es que ofrece una referencia ya entrenada y registrada con la cual comparar ajustes y alternativas. La elección definitiva deberá equilibrar omisiones, localización y costo de ejecución. No se presupone superioridad frente a otras arquitecturas ni se trasladan comparaciones del desarrollador a la Raspberry Pi sin repetir la medición.

### 2.6 Métricas y consecuencias de los errores

La precisión se expresa como TP/(TP + FP), y la sensibilidad como TP/(TP + FN), donde TP son detecciones correctamente asociadas a un agave, FP son detecciones falsas y FN son agaves omitidos. El F1 combina precisión y sensibilidad mediante su media armónica. La intersección sobre unión, IoU, relaciona el área compartida por dos cajas con el área de su unión [13].

El AP resume la curva precisión-sensibilidad para un criterio de coincidencia. AP50 utiliza IoU de 0.50; AP50-95 promedia resultados con umbrales de IoU de 0.50 a 0.95 en incrementos de 0.05 [13]. Estas medidas integran reconocimiento y localización bajo reglas de evaluación, pero no representan directamente probabilidad de daño o de protección de una planta.

En el sistema propuesto, las métricas visuales se complementan con protección oportuna por evento. Una planta puede omitirse en algunos fotogramas y quedar protegida por una detección previa; también puede detectarse correctamente demasiado tarde. Por ello, el porcentaje de falsos negativos por imagen y el porcentaje de plantas expuestas a una habilitación indebida deben informarse como variables diferentes.

El puntaje de confianza tampoco se tratará como probabilidad calibrada de ausencia de riesgo. El umbral regula qué detecciones se conservan; reducirlo puede recuperar plantas y producir más falsas detecciones. Ese intercambio deberá medirse en validación y comprobarse en la prueba reservada.

### 2.7 Seguimiento temporal y conteo

BoT-SORT es un método de seguimiento multiobjeto que combina información de movimiento y apariencia, e incorpora compensación del movimiento de cámara en su formulación [14]. Su uso en agave exige revisar la configuración, pues no todos los componentes tienen que estar activos en una implementación concreta. La evaluación original sobre personas tampoco acredita directamente su desempeño sobre plantas.

Un identificador temporal permite relacionar detecciones sucesivas y registrar cruces por una línea. En este trabajo, esa información puede ayudar a estudiar continuidad y oportunidad de protección. Sin embargo, un seguimiento puede fragmentarse, intercambiar identidades o conservar una trayectoria incorrecta. El conteo de eventos no debe interpretarse como número verdadero de plantas sin una referencia manual independiente.

Para apoyar la protección, una trayectoria deberá conservar su antigüedad y un criterio de expiración. Mantener indefinidamente una región predicha produciría exclusiones innecesarias; eliminarla ante una sola omisión podría perder protección. El tiempo de persistencia será un parámetro de validación, no una garantía inherente al algoritmo.

### 2.8 Geometría de protección y sincronización

La conversión de percepción a tratamiento necesita una representación espacial adecuada, como muestra el trabajo de localización para tratamientos específicos de Lottes et al. [8]. En esta tesis se propone representar cada detección mediante una región ampliada y compararla con la zona de intervención, ambas expresadas en las mismas coordenadas.

Sea W la región autorizada para trabajar y sea P(t) la unión de regiones de agave protegidas en el instante t. La región candidata a intervención será W menos P(t). Esta diferencia geométrica no clasifica el contenido restante: únicamente expresa dónde no se ha establecido una exclusión a partir de la información disponible. La habilitación también dependerá de la vigencia de los datos y del estado operativo definido.

Como modelo cinemático inicial, si d es la distancia útil entre observación y actuación y v es una velocidad constante, el tiempo disponible se aproxima por d/v. Para que exista anticipación, la suma de latencia de adquisición, inferencia, comunicación y respuesta mecánica, más una reserva temporal, deberá ser menor que ese tiempo disponible. La expresión es un criterio propuesto para el diseño y deberá ajustarse cuando cambien la velocidad o la geometría.

No se asignará un margen fijo en centímetros a partir de cajas en píxeles sin calibración. Además, una transformación del plano del suelo no describe automáticamente las puntas de hojas elevadas. La validación geométrica deberá considerar la región de la planta que puede interceptar el implemento. Mientras no se cuente con esta relación, los resultados se expresarán en coordenadas de imagen y eventos simulados.

### 2.9 Procesamiento embebido y dominio de operación

El procesamiento embebido sitúa la inferencia en el equipo asociado a la cámara y al módulo de salida. Su utilidad depende de que el proceso completo responda antes del evento que debe controlar. El rendimiento expresado en imágenes por segundo informa sobre capacidad de procesamiento; la latencia y la antigüedad del fotograma describen la oportunidad de una decisión concreta. Un flujo con imágenes acumuladas puede entregar detecciones correctas de una posición que ya pasó.

El ensayo local de Raspberry Pi registró 60 inferencias sobre diez imágenes, después de tres llamadas de calentamiento. El máximo de memoria RSS del proceso fue de 482 MiB y no se observó uso de swap [16]. Estas mediciones apoyan la viabilidad de ejecutar ese modelo bajo la configuración probada, pero no demuestran estabilidad prolongada ni sincronización de un implemento.

El dominio de operación deberá describir perspectiva, iluminación, condiciones de maleza, visibilidad del agave y rango de movimiento admitido. La evaluación conjunta de reconocimiento, protección y latencia permitirá decidir cuándo habilitar el sistema y cuándo limitar su intervención. Así, la justificación del modelo queda vinculada a resultados medibles en el entorno de interés.

## Referencias

[1] A. McBratney, B. Whelan, T. Ancev y J. Bouma, “Future Directions of Precision Agriculture”, Precision Agriculture, vol. 6, pp. 7-23, 2005. https://doi.org/10.1007/s11119-005-0681-8

[2] P. Figueroa Castro, Identificación y control químico postemergente de malezas en agaves alcoholígenos en Guerrero. Tesis de Ingeniero Agrónomo Fitotecnista, Colegio Superior Agropecuario del Estado de Guerrero, Cocula, Guerrero, 2007.

[3] A. Wang, W. Zhang y X. Wei, “A review on weed detection using ground-based machine vision and image processing techniques”, Computers and Electronics in Agriculture, vol. 158, pp. 226-240, 2019. https://doi.org/10.1016/j.compag.2019.02.005

[4] H.-R. Qu y W.-H. Su, “Deep Learning-Based Weed–Crop Recognition for Smart Agricultural Equipment: A Review”, Agronomy, vol. 14, núm. 2, art. 363, 2024. https://doi.org/10.3390/agronomy14020363

[5] B. Melander, B. Lattanzi y E. Pannacci, “Intelligent versus non-intelligent mechanical intra-row weed control in transplanted onion and cabbage”, Crop Protection, vol. 72, pp. 1-8, 2015. https://doi.org/10.1016/j.cropro.2015.02.017

[6] J. Espinoza-Hernández, G. de J. López-Canteñs, I. L. López-Cruz y E. Romantchik-Kriuchkova, “Agave plant density using convolutional neural networks on aerial imagery”, Agrociencia, vol. 57, núm. 7, 2023. https://doi.org/10.47163/agrociencia.v57i7.2970

[7] H. Wang et al., “Deep learning-based target spraying control of weeds in wheat fields at tillering stage”, Frontiers in Plant Science, vol. 16, art. 1540722, 2025. https://doi.org/10.3389/fpls.2025.1540722

[8] P. Lottes, J. Behley, N. Chebrolu, A. Milioto y C. Stachniss, “Joint Stem Detection and Crop-Weed Classification for Plant-specific Treatment in Precision Farming”, prepublicación, 2018. https://doi.org/10.48550/arXiv.1806.03413

[9] J. Redmon, S. Divvala, R. Girshick y A. Farhadi, “You Only Look Once: Unified, Real-Time Object Detection”, versión revisada de prepublicación, 2016. https://doi.org/10.48550/arXiv.1506.02640

[10] G. Jocher, J. Qiu, M. Liu, S. Lyu, F. C. Akyon y M. E. Kalfaoglu, “Ultralytics YOLO26: Unified Real-Time End-to-End Vision Models”, prepublicación, 2026. https://doi.org/10.48550/arXiv.2606.03748

[11] Ultralytics, “Ultralytics YOLO26” y “Understanding End-to-End Detection in Ultralytics YOLO26”, documentación técnica. Consulta: 5 de octubre de 2026. https://docs.ultralytics.com/models/yolo26/ y https://docs.ultralytics.com/guides/end2end-detection/

[12] I. Goodfellow, Y. Bengio y A. Courville, Deep Learning. MIT Press, 2016. https://www.deeplearningbook.org/

[13] R. Padilla, W. L. Passos, T. L. B. Dias, S. L. Netto y E. A. B. da Silva, “A Comparative Analysis of Object Detection Metrics with a Companion Open-Source Toolkit”, Electronics, vol. 10, núm. 3, art. 279, 2021. https://doi.org/10.3390/electronics10030279

[14] N. Aharon, R. Orfaig y B.-Z. Bobrovsky, “BoT-SORT: Robust Associations Multi-Pedestrian Tracking”, prepublicación, 2022. https://doi.org/10.48550/arXiv.2206.14651

[15] R. E. Venegas Reyes, Avances de Proyecto, presentación de avance de tesis, Universidad Autónoma de Zacatecas, 30 de junio de 2026; y Reporte de avance de tesis, documento interno sin fecha explícita. Registros complementarios del proyecto: benchmark/agave_benchmark.csv y paper/insumos_paper.md.

[16] Proyecto de detección de agave, Prueba de YOLO26s en Raspberry Pi 4 de 2 GB, informe técnico interno, 21 de septiembre de 2026. Archivos: rpi_benchmark/RESULTADO.md y rpi_benchmark/results_threads4.json.
