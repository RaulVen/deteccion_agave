Vas bien en el enfoque: la introducción, el problema y la justificación ya plantean identificar el agave para orientar su protección durante el deshierbe. La tarea pendiente es hacer que portada, objetivos, hipótesis y metodología expresen ese mismo propósito y correspondan a los experimentos realizados. El documento todavía conserva elementos del protocolo de detección de maleza y promesas de funcionamiento que no están validadas.

Estas son notas de revisión del archivo **Tesis_Lumat_Cap1.pdf**, con corte al 27 de octubre de 2026. No se modificó el original. Se contrastó con las auditorías locales de modelos, datos, sistema embebido y bibliografía.

## 1. Cambios necesarios antes de cerrar el capítulo

| Ubicación | Hallazgo | Cambio propuesto |
|---|---|---|
| Página física 1, portada sin numeración | Conserva «Detección de maleza», «Protocolo» y diciembre de 2025. | Actualizar al objeto agave, naturaleza del documento y fecha de la versión presentada. |
| Página física 3 / impresa 2 | Introducción coherente con proteger el cultivo, pero presenta tiempo real y bajo costo sin criterios. | Formularlos como aspectos por evaluar; separar detección en imagen de localización física. |
| Página física 4 / impresa 3 | Estado del arte con citas incompletas y Flores fechado en 2019. | Corregir a 2021, resolver McBratney y añadir las cuatro referencias ausentes. |
| Página física 5 / impresa 4 | Hipótesis promete precisión y velocidad «suficientes» y reducción del riesgo. | Definir una comparación comprobable; reservar la protección física para ensayos específicos. |
| Página física 6 / impresa 5 | Objetivos y metodología mencionan YOLOv16, detección de maleza y activación a partir de ella. | Usar YOLO26n/YOLO26s y una clase objetivo, agave. Reformular la salida como información para protección. |
| Página física 7 / impresa 6 | Salida hacia actuadores basada en posición de maleza. | Describir coordenadas del agave, regiones de exclusión y condiciones de comunicación pendientes. |
| Página física 8 / impresa 7 | «2 Bibliografía» ocupa el siguiente capítulo. | Reservar capítulo 2 para Marco teórico y colocar Bibliografía al final de la tesis. |

## 2. Qué avances puede reconocer ya el escrito

Los nuevos modelos siguen detectando **una clase: agave**. La maleza forma parte del contexto de las imágenes; no hay una segunda clase etiquetada como maleza. El conjunto combinado tiene 2064 imágenes activas y 13611 cajas, más 166 imágenes reservadas. Se completaron cuatro entrenamientos de 150 épocas con YOLO26n y YOLO26s. Estos datos deben desarrollarse en metodología y resultados; en la introducción basta describir la ampliación a escenas con maleza.

La configuración de referencia a entrada 640 obtuvo precisión de 68.20 %, recall de 62.52 %, mAP50 de 66.55 % y mAP50–95 de 24.32 % en la prueba interna. Son métricas de detección: **62.52 % de recall no equivale a 62.52 % de protección**, y una caja detectada no garantiza que todas las hojas queden fuera del alcance de la herramienta.

Existe un prototipo Raspberry Pi con un peso histórico y demostraciones de seguimiento con los pesos nuevos en computadora. No se verificó el despliegue de esos nuevos pesos en Raspberry ni el accionamiento real de un mecanismo de corte. Los 35 y 139 eventos de los videos recientes son cruces automáticos por identificador, sin conteo manual completo de referencia.

Tampoco hay resultados separados por maleza seca y húmeda. Puede mantenerse esa diferencia como condición que se desea estudiar, pero todavía no como comparación concluida. La partición histórica contiene fotogramas temporalmente próximos en distintos subconjuntos; por ello conviene reconocer la limitación de independencia y preparar evaluación externa antes de afirmar generalización amplia. La actualización del capítulo no necesita convertir estas limitaciones en una lista extensa: debe evitar afirmaciones que dependan de resultados aún inexistentes.

## 3. Texto listo para sustituir

### Título propuesto

**Detección de agaves mediante redes neuronales profundas para su protección durante el deshierbe autónomo**

Este título expresa la aplicación prevista sin afirmar que se desarrolló y validó todo el vehículo autónomo. Si la institución exige explicitar el cultivo joven, puede añadirse «de edad temprana» después de «agaves», siempre que esa condición se documente en las plantas fotografiadas.

### Objetivo general

Desarrollar y evaluar un sistema de visión artificial basado en redes neuronales profundas para detectar y localizar agaves en imágenes RGB de parcelas con presencia de maleza, y generar información visual que sirva de base para delimitar regiones de protección del cultivo durante el deshierbe autónomo, considerando el desempeño de detección y las condiciones de implementación en una plataforma embebida.

### Objetivos particulares

1. Construir y documentar un conjunto de imágenes RGB con anotaciones de agave, que incluya escenas con presencia de maleza y variaciones de iluminación, escala y oclusión, estableciendo la procedencia de los datos y los criterios de separación entre entrenamiento, validación y prueba.
2. Entrenar y comparar configuraciones de YOLO26n y YOLO26s mediante aprendizaje por transferencia, registrando hiperparámetros y seleccionando los pesos a partir del desempeño en validación.
3. Evaluar los modelos mediante precisión, recall, mAP50 y mAP50–95, e identificar omisiones, falsas detecciones y errores de localización; analizar las limitaciones de generalización y de representación de las condiciones de campo.
4. Implementar y evaluar el módulo de percepción en una Raspberry Pi, identificando la versión de los pesos, el formato de ejecución y el tamaño de entrada, y midiendo por separado la tasa de inferencia y la latencia del procesamiento disponible.
5. Diseñar y evaluar una representación de las detecciones que permita definir regiones de exclusión alrededor de los agaves y establecer los parámetros requeridos para su futura comunicación al mecanismo de deshierbe, delimitando las calibraciones y pruebas físicas necesarias para validar la protección del cultivo.

### Hipótesis propuesta para contrastar

El entrenamiento de un detector YOLO26 con imágenes que incorporan agaves en presencia de maleza aumentará la sensibilidad de detección del agave, expresada mediante recall, respecto al modelo histórico del proyecto, cuando ambos se evalúen sobre un mismo conjunto de prueba independiente y bajo iguales condiciones de inferencia.

Esta formulación permite observar si la mejora ocurre, sin inventar un umbral. **Todavía requiere una comparación controlada**: no basta contrastar el resultado histórico con el nuevo porque cambian los conjuntos de prueba. Es una hipótesis sobre percepción; la ausencia de daño mecánico necesita una validación adicional. La elección definitiva debe corresponder a las pruebas que se incluirán en la tesis.

### Alcance y limitaciones

El trabajo comprende la preparación de datos RGB, el entrenamiento y la evaluación de detectores de una clase objetivo —agave—, así como el estudio de su implementación embebida y de las salidas visuales necesarias para apoyar la protección del cultivo. Las coordenadas obtenidas inicialmente pertenecen al plano de la imagen; su conversión a posiciones físicas y su relación con la herramienta requieren calibración. El seguimiento y el conteo por cruce de línea se consideran funciones auxiliares del módulo de percepción.

La presencia de maleza en el fondo no implica su clasificación explícita. Las condiciones de maleza seca y húmeda se incorporarán como categorías de evaluación cuando exista información suficiente para documentarlas. El diseño mecánico completo, la navegación autónoma y la demostración de corte sin daño quedan fuera de los resultados comprobados en esta etapa. La propuesta de regiones de exclusión no constituye por sí misma una garantía de protección física: su efectividad dependerá de la geometría de la herramienta, la incertidumbre de localización, el movimiento y la respuesta del sistema.

## 4. Bibliografía y redacción

En la página física 4 / impresa 3 faltan citas y entradas finales para **McBratney, Flores, Xiang y Matadamas**. Correcciones verificadas:

- Flores corresponde a **2021**; F1 = 0.96 está respaldado, con imágenes aéreas. [Artículo original](https://doi.org/10.3390/drones5010004).
- Xiang et al. (2024) justifican la estrategia de detectar el cultivo para evitarlo durante el deshierbe. La propuesta concreta del proyecto debe presentarse como aplicación de ese fundamento. [Artículo original](https://doi.org/10.3389/fpls.2024.1361002).
- Matadamas et al. (2024) reportan las cifras citadas, pero estudian plantas de cuatro años y cinco clases visuales. Conservar «mAP reportada» sin añadir un umbral IoU no verificado. [Artículo original](https://doi.org/10.3390/agriculture14122199).
- Sustituir la clave visible de McBratney por una cita resuelta y añadir la referencia completa. Revisar la frase entre comillas antes de atribuirla literalmente. [Ficha editorial](https://doi.org/10.1007/s11119-005-0681-8).

Completar también autores y DOI de Espinoza-Hernández et al. (2023): [10.47163/agrociencia.v57i7.2970](https://doi.org/10.47163/agrociencia.v57i7.2970). La entrada [1], «E. García», carece del nombre de la publicación; requiere recuperar el original. Las afirmaciones de costos, pérdidas y accesibilidad en Zacatecas necesitan fuentes locales o una redacción menos categórica.

Corregir «Edaurdo» por **Eduardo** en la portada, previa confirmación del nombre; «riego de daño» por **riesgo de daño**; «Rasberry» por **Raspberry**; «deshiervador» por **deshierbador**; «aprenidizaje» por **aprendizaje**; «RetnaNet» por **RetinaNet** y «Agave anfustifolia» por ***Agave angustifolia***. Separar los años de los apellidos y revisar expresiones como «para mejora tener» y «requieren una considerable de mano de obra».

## 5. Continuación con el capítulo 2

El Marco teórico debe explicar agricultura de precisión y deshierbe selectivo; percepción RGB y dificultades del campo; detección de objetos, CNN y YOLO26; transferencia de aprendizaje y preparación de datos; IoU y métricas; seguimiento temporal; procesamiento embebido; y relación entre detección, incertidumbre y protección. Los tamaños del dataset, las cuatro corridas y sus cifras pertenecen a los capítulos posteriores. Mantener esta separación permite fundamentar el sistema antes de describir cómo se construyó y qué resultados obtuvo.

Se preparó un [borrador editable del capítulo 2](Capitulo_2_Marco_teorico_2026-10-27.md) y su PDF. Las 16 referencias de ese borrador tienen numeración propia para facilitar su revisión. Al integrarlo con el capítulo 1 se debe unificar la bibliografía, resolver duplicados como Xiang y Qu/Su y regenerar la numeración de las citas. No se sustituyeron las referencias originales del autor.
