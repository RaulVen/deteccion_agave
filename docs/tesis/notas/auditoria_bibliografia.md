# Auditoría bibliográfica de Tesis_Lumat_Cap1.pdf

Fecha de revisión: 27 de octubre de 2026. Documento revisado: `C:/Users/iceve/Downloads/Tesis_Lumat_Cap1.pdf`, a través del texto extraído en `capitulo1.txt`. No se modificó el PDF. Las páginas indicadas son las páginas físicas del PDF, no la numeración impresa.

## Hallazgos prioritarios

1. **Faltan cuatro entradas bibliográficas.** En el estado del arte (p. 4 del PDF) se describen McBratney, Flores, Xiang y Matadamas, pero la bibliografía final solo tiene diez entradas y no incluye ninguna de esas cuatro. Hay que incorporar las referencias, citarlas con el mismo sistema numérico y regenerar la numeración automáticamente.
2. **Hay una cita sin resolver.** La cadena `mcbratney_future_2005` aparece como texto. Debe sustituirse por una cita bibliográfica resuelta; no es parte del discurso académico.
3. **Flores está fechado incorrectamente.** Cambiar «2019 Flores et al.» por «2021 Flores et al.». El resultado F1 = 0.96 sí corresponde a ese trabajo. Es un antecedente de detección y conteo con imágenes aéreas, no de protección de plantas mediante un deshierbador terrestre.
4. **Matadamas está resumido de forma mayormente correcta, pero falta precisión.** Los valores 0.616/0.606/0.606 corresponden al conjunto de prueba. El texto consultado denomina la métrica mAP; no se verificó un umbral IoU que autorice llamarla mAP50 o mAP50–95. No compararla directamente con métricas propias bajo otro protocolo.
5. **La revisión de Xiang sí justifica el cambio de enfoque.** Respalda detectar el cultivo para que el mecanismo lo evite. Es fundamento bibliográfico, no evidencia de que el sistema de esta tesis ya evite daños.
6. **La referencia [9] está incompleta.** Añadir todos los autores, título correcto, volumen y DOI de Espinoza-Hernández et al.

## Referencias verificadas y correcciones

### Flores et al. (2021)

D. Flores, I. González-Hernández, R. Lozano, J. M. Vazquez-Nicolas y J. L. Hernandez Toral, «Automated Agave Detection and Counting Using a Convolutional Neural Network and Unmanned Aerial Systems», *Drones*, vol. 5, núm. 1, art. 4, 2021. DOI: [10.3390/drones5010004](https://doi.org/10.3390/drones5010004).

La editorial registra publicación el 1 de enero de 2021. El resumen informa F1 = 0.96 para su propuesta frente a 0.57 para Haar, utilizando datos aéreos UAV. Corrección sugerida: «En 2021, Flores et al. propusieron un método de detección y conteo de agaves a partir de imágenes aéreas y una red neuronal convolucional, con F1 = 0.96 en su evaluación». Añadir la cita y evitar presentar ese resultado como desempeño terrestre o embebido comprobado.

Fuentes primarias: [artículo](https://www.mdpi.com/2504-446X/5/1/4) y [número de la revista, fecha y resumen](https://www.mdpi.com/2504-446X/5/1).

### Xiang et al. (2024)

M. Xiang, M. Qu, G. Wang, Z. Ma, X. Chen, Z. Zhou, J. Qi, X. Gao, H. Li y H. Jia, «Crop detection technologies, mechanical weeding executive parts and working performance of intelligent mechanical weeding: a review», *Frontiers in Plant Science*, vol. 15, art. 1361002, 2024. DOI: [10.3389/fpls.2024.1361002](https://doi.org/10.3389/fpls.2024.1361002).

La sección 3 distingue dos modos: identificar el cultivo y ejecutar la evasión al detectarlo, o identificar maleza y actuar cuando se detecta. Las conclusiones favorecen la localización del cultivo por su disposición más uniforme, bajo el contexto que examinan. El párrafo de la tesis es defendible si se añade la cita. Conviene formular la zona de protección específica del agave como una decisión del proyecto, cuya geometría y desempeño requieren evaluación.

Fuente primaria: [artículo completo, sección 3 y conclusiones](https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2024.1361002/full).

### Matadamas et al. (2024)

I. Matadamas, E. Zamora y T. Aquino-Bolaños, «Detection and Classification of Agave angustifolia Haw Using Deep Learning Models», *Agriculture*, vol. 14, núm. 12, art. 2199, 2024. DOI: [10.3390/agriculture14122199](https://doi.org/10.3390/agriculture14122199).

Se confirman 333 imágenes, 1317 plantas anotadas, cinco clases y cinco modelos. YOLOv7 obtuvo mAP = 0.616 en prueba; YOLOv7-tiny y YOLOv8n, 0.606. La fuente denomina YOLOv8 a YOLOv8n. La cámara Canon Rebel T3i se ubicó con eje paralelo al suelo, al nivel del objeto; el cultivo tenía cuatro años. Por ello es antecedente terrestre pertinente, pero no valida por sí mismo agaves jóvenes entre maleza ni control mecánico. Corregir «anfustifolia» por *angustifolia*, «RetnaNet» por RetinaNet y «aprenidizaje» por aprendizaje. La sección de métricas consultada no permite identificar inequívocamente el umbral IoU: conservar «mAP reportada por los autores».

Fuente primaria: [artículo, apartados 2.1, 2.4 y 3](https://www.mdpi.com/2077-0472/14/12/2199). El acceso directo arrojó 429; se consultó el contenido de la página editorial recuperado por el buscador. No se mezcló con el resumen de congreso, que reporta otra cifra (0.619).

### McBratney et al. (2005)

A. McBratney, B. Whelan, T. Ancev y J. Bouma, «Future Directions of Precision Agriculture», *Precision Agriculture*, vol. 6, pp. 7–23, 2005. DOI: [10.1007/s11119-005-0681-8](https://doi.org/10.1007/s11119-005-0681-8).

La ficha editorial confirma autores, título, año, páginas y DOI. No se verificó en el texto íntegro la atribución exacta entre comillas «cantidad correcta, en el lugar correcto y en el momento oportuno». Usar una paráfrasis sustentada o revisar el pasaje y su página antes de mantener una cita literal. El resumen sí trata limitaciones y líneas futuras de agricultura de precisión, incluidos sistemas de apoyo a decisiones y variación temporal.

Fuente primaria: [editorial Springer](https://link.springer.com/article/10.1007/s11119-005-0681-8).

### Espinoza-Hernández et al. (2023), referencia [9]

J. Espinoza-Hernández, G. de J. López-Canteñs, I. L. López-Cruz y E. Romantchik-Kriuchkova, «Agave plant density using convolutional neural networks on aerial imagery», *Agrociencia*, vol. 57, núm. 7, 2023. DOI: [10.47163/agrociencia.v57i7.2970](https://doi.org/10.47163/agrociencia.v57i7.2970).

La ficha de la revista confirma YOLOv4 y YOLOv4-tiny, imágenes RGB aéreas, confianza 0.25 y umbral IoU 0.50. Es pertinente conservarlo como antecedente aéreo. El título del borrador añade «RGB» y cambia «on» por «and»; normalizar al título publicado. No inferir tiempo real en Raspberry Pi a partir de la existencia de una variante tiny.

Fuente primaria: [ficha de Agrociencia](https://agrociencia-colpos.org/index.php/agrociencia/article/view/2970).

### Qu y Su (2024), referencia [10]

La identificación bibliográfica es correcta: H.-R. Qu y W.-H. Su, *Agronomy* 14(2), 363, DOI [10.3390/agronomy14020363](https://doi.org/10.3390/agronomy14020363). Su revisión examina reconocimiento cultivo–maleza, aplicaciones, limitaciones ambientales y modelos ligeros. La frase del borrador que generaliza que YOLO ligero permite tiempo real en plataformas embebidas debería matizarse: la elección de un modelo ligero requiere medir velocidad y precisión en el hardware concreto. La revisión ofrece fundamento general, no prueba de desempeño del prototipo.

Fuente primaria: [artículo completo](https://www.mdpi.com/2073-4395/14/2/363).

### Weed25 (2022), referencia [8]

La afirmación central del borrador es correcta: conjunto de 25 especies y evaluación de YOLOv3, YOLOv5 y Faster R-CNN. La fuente declara IoU = 0.5. Si se incorporan cifras, denominarlas mAP50: 91.80 %, 92.40 % y 92.15 %, respectivamente, según tabla 4. Es un conjunto de detección de maleza; no sustituye a la evaluación propia de protección de agave.

Fuente primaria: [Wang et al., artículo y tabla 4](https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2022.1053329/full).

## Ajustes editoriales y límites de esta revisión

- La cronología «2010–2014» usa como apoyo una revisión de 2021, lo cual puede ser válido si se presenta como síntesis retrospectiva. Si se narran hitos concretos, citar estudios originales y sus años.
- [1] carece del nombre de la publicación o editorial. No puede identificarse inequívocamente solo con «E. García, Agricultura de precisión, no. 8, 45–52, 2008». Completarla desde el documento original o sustituirla por una fuente plenamente identificable.
- Las afirmaciones regionales sobre pérdidas, costos e inaccesibilidad económica necesitan fuentes pertinentes y delimitación. Una referencia divulgativa sobre agave azul no demuestra por sí sola magnitudes de pérdida en Zacatecas.
- Los resultados bibliográficos de plantas adultas, imágenes aéreas o cinco clases sanitarias deben distinguirse del experimento propio de una clase agave entre maleza.
- No se verificaron exhaustivamente las diez referencias originales. La auditoría priorizó las cuatro adiciones ausentes, la referencia [9] incompleta y las dos afirmaciones de modelos/datasets más relacionadas con el cambio de enfoque.
- La denominación «YOLOv16» aparece dos veces en objetivos/metodología. Debe contrastarse con los archivos y entrenamientos reales del proyecto; no cambiarla por una versión supuesta solo a partir de la bibliografía.
