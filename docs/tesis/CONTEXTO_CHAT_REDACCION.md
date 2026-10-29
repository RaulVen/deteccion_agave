# Contexto para continuar el chat de redacción

Resumen preparado el **28 de octubre de 2026** a partir de las solicitudes y entregas del chat **«Redactar capítulo 1 sobre detección»**. Conserva las decisiones relevantes para continuar en otra computadora; no es una transcripción completa ni implica que el chat nuevo tenga acceso al historial original.

## Qué quiere el autor

Dedicar el chat de redacción exclusivamente al escrito de la tesis. En esta computadora se redacta; los entrenamientos, preparación de datos y trabajo con cámara/Raspberry se realizan en la computadora de cómputo. Ambas utilizan este repositorio y `main` para compartir archivos.

La tesis cambió de enfoque: **identificar y localizar los agaves para que un deshierbador autónomo pueda evitar cortarlos o dañarlos**. La maleza constituye el entorno del cultivo. Cuando el autor habla de condiciones secas y húmedas se refiere a **maleza seca y maleza húmeda**, no al agave seco. La finalidad del sistema no debe confundirse con una protección mecánica ya demostrada.

Se deben aprovechar las referencias pertinentes del protocolo y añadir fuentes verificadas para justificar el cambio de enfoque y la red neuronal. No inventar citas, experimentos, umbrales de desempeño ni resultados.

## Preferencias de redacción expresadas en el chat

- Tono natural, directo y cercano al capítulo escrito por el autor, manteniendo el rigor académico. Usar su PDF como referencia de voz y nivel de explicación.
- Explicar los conceptos para lectores que no conocen visión artificial ni redes neuronales: introducir cada término antes de usarlo y apoyar las fórmulas con ejemplos de agaves.
- Explicar a grandes rasgos la estructura de YOLO y el recorrido de la imagen por backbone, neck y head.
- Desarrollar con detalle confianza, IoU, aciertos, falsas detecciones, omisiones, precisión, recall, F1, AP, mAP, matriz de confusión y pérdidas. Distinguir conceptos y no presentar ejemplos didácticos como mediciones reales.
- Explicar el aumento de datos, cómo transforma las imágenes y etiquetas, y cuáles transformaciones se emplearon realmente en los experimentos.
- Conservar el desarrollo de seguimiento y cruce de línea, que el autor consideró adecuado.
- El autor dejó la extensión al criterio del contenido; no impuso un número fijo de páginas. Mantener la estructura académica y unificar las citas numéricas al integrar capítulos.

## Documentos y punto donde quedó el trabajo

| Documento | Estado y uso |
|---|---|
| [Capítulo 1 aportado por el autor](insumos_usuario/Tesis_Lumat_Cap1.pdf) | Archivo usado para la revisión del 27 de octubre. Es la referencia del texto del autor; no fue corregido por aquella revisión. Copiado sin modificar desde el archivo local que se compartió en el chat. |
| [Protocolo original](insumos_usuario/Protocolo_lumat.pdf) | Antecedente aportado por el autor. Contiene el enfoque previo; consultar su estructura y referencias sin restablecer la detección de maleza como objetivo. Copiado sin modificar. |
| [Revisión del capítulo 1](Revision_capitulo_1_2026-10-27.md) | Diagnóstico del PDF del autor y propuestas de título, objetivos, hipótesis, alcance y correcciones bibliográficas. Son propuestas: no consta su incorporación ni aprobación definitiva. |
| [Borrador generado de capítulo 1 y marco teórico](Capitulo_1_y_marco_teorico_agave.md) | Versión anterior preparada el 5 de octubre tras incorporar el protocolo. No sustituye al PDF del autor revisado después. Incluye un marco teórico anterior que no debe duplicarse al integrar el capítulo 2 ampliado. |
| [Capítulo 2 ampliado](Capitulo_2_Marco_teorico_ampliado.md) y [PDF](Capitulo_2_Marco_teorico_ampliado.pdf) | Última entrega del chat, posterior a la petición de mayor claridad. Se entregaron 19 páginas, 25 referencias y dos figuras. Esta es la versión de partida del capítulo 2. |
| [Capítulo 2 del 27 de octubre](Capitulo_2_Marco_teorico_2026-10-27.md) | Borrador anterior de 8 páginas y 16 referencias; conservar como antecedente. |

La última solicitud fue mejorar el tono y ampliar YOLO, métricas y aumento de datos. La última respuesta entregó la versión ampliada. No consta una revisión posterior del autor ni la aprobación final del escrito completo. No hay un documento único final que ya integre ambos capítulos.

## Qué falta resolver

1. Aplicar, previa revisión del autor, las correcciones del capítulo 1: alinear portada, problema, hipótesis, objetivos y metodología con detectar agave y con los experimentos realmente realizados. En el PDF revisado aún aparecían detección de maleza y YOLOv16.
2. Revisar el capítulo 2 ampliado con el autor y armonizar su tono y estructura con el capítulo 1. Mantener las explicaciones accesibles que solicitó.
3. Completar las referencias pendientes del capítulo 1 y unificar la bibliografía y numeración entre capítulos. Las referencias del capítulo 2 tienen numeración propia; no pegarlas sin resolver duplicados.
4. Mantener los fundamentos en el marco teórico y desarrollar protocolos, tamaños de datasets y resultados en los capítulos correspondientes.

Estas son tareas pendientes documentadas, no autorización para reemplazar de una vez todos los archivos. Al retomar, resumir brevemente el estado y seguir la indicación actual del autor.

## Contexto computacional que limita las afirmaciones

Leer el [contexto técnico del proyecto](Contexto_del_proyecto_para_redaccion_2026-10-27.md), las [auditorías](notas/) y la [evidencia compartida](../resultados/README.md) antes de describir resultados.

- El detector tiene una clase objetivo: agave. La maleza es contexto, no una segunda clase anotada.
- Se documentaron cuatro entrenamientos nuevos de 150 épocas. No comparar sus cifras directamente con el benchmark histórico como una mejora controlada: cambió el conjunto de prueba.
- Las pruebas Raspberry documentadas emplean el modelo histórico. No consta despliegue de los pesos nuevos ni validación física de corte sin daño.
- Los conteos por cruce de línea son resultados automáticos sin referencia manual completa; no equivalen a exactitud de conteo demostrada.
- No hay resultados separados sistemáticamente por maleza seca/húmeda. No detectar un agave tampoco demuestra que sea seguro cortar en esa región.

Conservar esas distinciones sin llenar el escrito de advertencias repetitivas. Las cifras concretas y su procedencia están en los documentos enlazados.

## Cómo continuar en la otra computadora

Actualizar la copia del repositorio conservando cualquier trabajo local y abrir su carpeta como proyecto. Leer este resumen, el [índice de redacción](README.md), el PDF del autor y la revisión del capítulo 1. Después consultar el capítulo 2 ampliado y el contexto técnico según la tarea solicitada.

Editar dentro de este repositorio. Las copias antiguas en `Documents/ChatGPT/tesis` de la computadora de cómputo no se sincronizan automáticamente. No entrenar, modificar el hardware ni regenerar documentos solo para cargar contexto. La [guía de sincronización](../SINCRONIZACION.md) describe cómo guardar cambios y compartirlos mediante `main`.

Los otros materiales originales mencionados en el chat —presentación de avances de junio, reporte de avance e imagen de un índice— no forman parte de esta nueva carpeta de insumos. Si una tarea requiere revisar exactamente alguno de ellos, deberá obtenerse el original; no asumir que este resumen lo reproduce.
