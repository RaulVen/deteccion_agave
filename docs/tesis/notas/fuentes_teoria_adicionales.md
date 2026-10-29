# Fuentes primarias adicionales para el capítulo 2

Verificación web: 27 de octubre de 2026. Se consultaron fuentes del autor/editorial, actas originales y documentación oficial. Estas referencias fundamentan conceptos; no certifican resultados del proyecto.

## 1. Calibración de cámara

**Referencia:** Zhang, Z. (2000). A flexible new technique for camera calibration. *IEEE Transactions on Pattern Analysis and Machine Intelligence, 22*(11), 1330–1334. DOI: [10.1109/34.888718](https://doi.org/10.1109/34.888718).

**Verificado:** autor, título, revista, año, volumen y páginas en la [ficha de Microsoft Research](https://www.microsoft.com/en-us/research/publication/a-flexible-new-technique-for-camera-calibration/); el DOI conduce al artículo IEEE 888718, cuya lectura directa pide verificación del navegador. El [artículo original, copia universitaria](https://cecas.clemson.edu/~stb/ece847/internal/classic_vision_papers/zhang_calibration_pami2000.pdf), identifica volumen 22, número 11, noviembre de 2000. La ficha Microsoft dice diciembre de 2000: evitar mes en la referencia para no reproducir esa discrepancia. El [reporte técnico del autor](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr98-71.pdf) es MSR-TR-98-71 (1998, revisiones posteriores), no debe confundirse bibliográficamente con el artículo de 2000.

**Soporte teórico:** calibración mediante un patrón plano observado en distintas orientaciones; estimación de parámetros intrínsecos y extrínsecos; modelado de distorsión radial y refinamiento no lineal. Sirve para explicar por qué coordenadas de una caja en píxeles no equivalen automáticamente a distancias físicas. Una homografía corresponde al plano modelado: no atribuirle una reconstrucción 3D completa de hojas fuera del plano.

**Aplicación prudente:** fundamentar la futura transformación cámara–zona de trabajo y la necesidad de calibración; no escribir que el proyecto ya fue calibrado porque los archivos revisados no lo demuestran.

## 2. ncnn y exportación

**Referencia del software según su propio CITATION.cff:** Ni, H., & The ncnn contributors. (2017). *ncnn* [Software]. Tencent. [Repositorio oficial](https://github.com/Tencent/ncnn). [Metadatos de citación oficiales](https://github.com/Tencent/ncnn/blob/master/CITATION.cff).

El CITATION.cff declara autor Hui Ni y colaboradores, publicación inicial 2017-06-30 y licencia BSD-3-Clause; no incluye DOI ni versión fija. Para metodología, agregar la versión local efectivamente utilizada (el respaldo declara NCNN 1.0.20260526), sin presentarla como la versión más reciente. En bibliografía de software puede citarse la versión utilizada además del repositorio y fecha de consulta.

**Soporte:** motor de inferencia orientado a despliegue móvil/embebido, ejecución CPU y soporte Vulkan, herramientas de conversión como pnnx y ausencia de dependencias externas de ejecución en el núcleo. El repositorio no demuestra la velocidad de este sistema ni garantiza equivalencia numérica de una exportación particular. [README oficial](https://github.com/Tencent/ncnn/blob/master/README.md).

**Referencia de documentación:** Ultralytics. (s. f.). *Ultralytics YOLO NCNN Export*. Recuperado el 27 de octubre de 2026, de [documentación oficial de exportación NCNN](https://docs.ultralytics.com/integrations/ncnn).

**Soporte vigente:** exportación `model.export(format="ncnn")`, carga del directorio exportado, inferencia y validación; argumento `imgsz` para tamaño de entrada, lote y precisión exportada. La documentación actual usa `quantize` y marca `half` como obsoleto para esta exportación. Conviene separar teoría general de parámetros de la versión concreta del experimento.

**Precisión numérica:** la documentación distingue FP32 de los pesos exportados de la aritmética que el runtime puede elegir en hardware compatible. El ejecutor local configura CPU, dos hilos y `use_vulkan_compute=False`, pero no fija explícitamente todas las opciones FP16. Para el escrito es más exacto «exportación de pesos FP32 y ejecución NCNN en CPU» que asegurar toda operación interna en FP32 sin una comprobación adicional. Esto no afecta a las pruebas de video CUDA 26-oct, que sí declaran `half=false`.

**End-to-end:** la página de integración NCNN revisada no especifica el estado de esa rama para la exportación histórica. La afirmación sobre deshabilitación en este proyecto se sostiene con `rpi_restore/best_ncnn_model/metadata.yaml` (`end2end:false`) y los registros locales, no con una generalización sobre toda versión de NCNN.

## 3. Redes profundas y CNN

**Referencia:** LeCun, Y., Bengio, Y., & Hinton, G. (2015). Deep learning. *Nature, 521*, 436–444. DOI: [10.1038/nature14539](https://doi.org/10.1038/nature14539).

**Verificado:** autores, revista, volumen, páginas y DOI en los metadatos de la editorial; publicación en línea el 27 de mayo de 2015, edición del 28 de mayo de 2015. La página directa Nature presentó barrera de redirección, pero sus metadatos están disponibles en búsqueda y se consultó la [copia publicada en la web de Hinton](https://www.cs.toronto.edu/~hinton/absps/NatureDeepReview.pdf).

**Soporte:** aprendizaje de representaciones por múltiples capas, retropropagación, convoluciones, conexiones locales y compartición de pesos. Adecuado para explicar extracción jerárquica de características visuales. Es una revisión fundacional; no es la fuente original de YOLO26 ni prueba que la red concreta tolere cualquier condición de maleza, iluminación u oclusión.

## 4. Transferencia de aprendizaje

**Referencia:** Yosinski, J., Clune, J., Bengio, Y., & Lipson, H. (2014). How transferable are features in deep neural networks? En *Advances in Neural Information Processing Systems, 27*, 3320–3328. [Actas originales](https://papers.nips.cc/paper_files/paper/2014/hash/532a2f85b6977104bc93f8580abbb330-Abstract.html).

**Verificado:** autores y trabajo en las actas; volumen y páginas también en el [registro arXiv del autor](https://arxiv.org/abs/1411.1792). El DOI [10.48550/arXiv.1411.1792](https://doi.org/10.48550/arXiv.1411.1792) identifica el preprint arXiv, no un DOI editorial de las actas; puede omitirse si se cita la versión de NeurIPS.

**Soporte:** características de capas iniciales más generales y posteriores más específicas; transferencia condicionada por distancia entre tareas y coadaptación de neuronas; posibilidad de mejorar generalización con inicialización preentrenada y ajuste posterior. Justifica adoptar pesos preentrenados y adaptarlos a agave, pero no garantiza mejora frente a entrenar desde cero sin comparación propia.

## Propuesta de ubicación

- CNN y representación visual: LeCun et al. 2015.
- Entrenamiento y ajuste de pesos preentrenados: Yosinski et al. 2014.
- Coordenadas, proyección y relación con la herramienta: Zhang 2000.
- Despliegue embebido, formato y runtime: Ni y colaboradores; documentación Ultralytics, separando soporte bibliográfico y evidencia experimental local.

Estas cinco entradas complementan YOLO26, métricas de detección y seguimiento; no reemplazan sus referencias específicas.
