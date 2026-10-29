# Notas para revisar el borrador con el asesor

Fecha de preparación: 5 de octubre de 2026.

## Alcance de la redacción

El documento principal contiene un capítulo 1 desarrollado con la estructura de la imagen proporcionada, un desarrollo separado del capítulo 2 sobre los fundamentos necesarios para el nuevo enfoque y una bibliografía común. Es un borrador académico para revisión. El título es una propuesta, no un cambio institucional ya aprobado. No se redactaron resumen ni summary porque describirían una tesis completa cuyos resultados finales aún no están disponibles.

La modificación solicitada gobierna el texto: detectar y proteger el agave frente a condiciones de maleza seca y húmeda. Las indicaciones antiguas de incorporar obligatoriamente una clase maleza se trataron como parte del enfoque anterior, no como instrucciones vigentes.

## Material recuperado

- Protocolo.pptx, localizado en Descargas. Antecedente consultado en la primera redacción. Posteriormente se incorporó Protocolo_lumat.pdf, el protocolo escrito de diciembre de 2025, aportado por el usuario.
- Avances de tesis Junio.pptx, fechado el 30 de junio de 2026: localización de parcela en Juchipila, agave de dos años y avances con YOLO26.
- Reporte de avance de tesis.pdf, siete páginas, sin fecha explícita: alcance anterior, datos, métricas y conteo.
- Repositorio C:/Users/iceve/Documents/github/deteccion de agave: benchmark/agave_benchmark.csv, paper/insumos_paper.md, paper/referencias_verificadas.md y evidencia/analisis_agave_tesis.md.
- Carpeta de trabajo actual: rpi_benchmark/RESULTADO.md y resultados del ensayo de septiembre de 2026.
- TESIS-AGAVE-MALEZAS-2007-PFC-LIGERA.pdf, localizada en Descargas: tesis de Pedro Figueroa Castro, 2007. Se emplea como antecedente agronómico histórico y no como recomendación actual de herbicidas.

## Referencias conservadas y añadidas

Se conservan del protocolo McBratney et al. (2005), Wang et al. (2019), Qu y Su (2024), Espinoza-Hernández et al. (2023) y Wang et al. (2025), con numeración reorganizada y títulos normalizados. El título correcto de Espinoza-Hernández es Agave plant density using convolutional neural networks on aerial imagery; se añadió el DOI.

Se incorporan Melander et al. (2015), para el reconocimiento del cultivo y deshierbe intrahilera; Lottes et al. (2018), para la relación entre localización y tratamiento; Redmon et al. (2016), para el fundamento de YOLO; Jocher et al. (2026) y la documentación de Ultralytics, para YOLO26; Goodfellow et al. (2016), para fundamentos de aprendizaje profundo; Padilla et al. (2021), para métricas; y Aharon et al. (2022), para BoT-SORT. Algunas ya estaban presentes en los insumos locales del artículo, aunque no en la bibliografía del protocolo.

Las prepublicaciones se identifican como tales. La referencia a documentación web incluye fecha de consulta porque su contenido puede cambiar. La explicación de YOLO26 no afirma que el experimento local usó MuSGD: los registros indican SGD. Tampoco afirma una ruta específica de inferencia con o sin NMS sin comprobar la versión instalada.

Las referencias incompletas E. García (2008) y Agenda técnica agrícola de Zacatecas no se usaron como soporte central. No se eliminaron de los archivos originales. La cita de Vijayakumar et al. (2025) quedó fuera del borrador para concentrar el argumento y no utilizar contenido que no se pudo inspeccionar suficientemente. Las referencias sobre resistencia a herbicidas y otros trabajos mencionados en diapositivas pueden reservarse para una revisión agronómica más amplia, si el asesor considera necesario desarrollarla.

## Comprobación de fuentes externas

- McBratney: página del editor https://link.springer.com/article/10.1007/s11119-005-0681-8
- Wang 2019: metadatos del DOI contrastados con Crossref; el uso en el texto se limita al tema y alcance de la revisión, sin cifras específicas.
- Qu y Su: metadatos y resumen depositado por el editor en Crossref, https://api.crossref.org/works/10.3390/agronomy14020363 . El acceso directo a MDPI no fue estable.
- Melander: resumen de Crop Protection y registro institucional de Aarhus https://pure.au.dk/portal/da/publications/intelligent-versus-non-intelligent-mechanical-intra-row-weed-cont/
- Espinoza-Hernández: artículo original https://agrociencia-colpos.org/index.php/agrociencia/article/download/2970/2261
- Wang 2025: texto de Frontiers https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2025.1540722/full
- Lottes, Redmon, Jocher y Aharon: fichas originales de arXiv enlazadas en las referencias del documento principal.
- Goodfellow: página oficial del libro https://www.deeplearningbook.org/
- Padilla: página de Electronics y repositorio del autor https://github.com/rafaelpadilla/Object-Detection-Metrics
- Ultralytics: documentación oficial enlazada en la referencia [11]. Sus rutas actuales no se atribuyen retrospectivamente a las versiones ya probadas.

## Puntos que requieren decisión experimental

1. Confirmar con el asesor el título y el alcance formal del cambio. La propuesta mantiene el diseño mecánico fuera del núcleo, pero incluye la generación y validación de señales.
2. Confirmar especie de agave y edad en futuras adquisiciones. El material recuperado permite afirmar dos años en la adquisición original, no en todas las fechas ni para cualquier parcela. El texto evita asignar Agave tequilana a la parcela sin verificación.
3. Definir cómo registrar maleza seca y húmeda. No confundir humedad superficial con tejido verde o senescente. Si se desea contenido de agua cuantitativo, incorporar un método de medición independiente.
4. Precisar mecanismo y geometría: región de planta que debe protegerse, ancho de trabajo, separación cámara-herramienta, velocidad y tiempos de actuación. Sin ello no procede inventar márgenes en centímetros, velocidades admisibles o niveles de protección.
5. Acordar el método básico de comparación y los criterios de aceptación antes de evaluar el conjunto final. Son propuestas metodológicas, no ensayos ya ejecutados.
6. Reservar datos nuevos e independientes para la evaluación definitiva: el conjunto histórico de prueba se utilizó para comparar corridas y no debe presentarse como prueba final ciega.
7. Revisar inconsistencias entre informes locales sobre cajas dentro de límites: paper/insumos_paper.md informa verdadero y evidencia/analisis_agave_tesis.md informa falso. El borrador no afirma que esa auditoría esté resuelta ni reutiliza sus conteos de cajas.

## Distinciones que conviene conservar

- Detectar agave no certifica que todo el resto de la imagen sea maleza.
- Una caja de detección no es una máscara de segmentación ni un contorno físico exacto.
- Precisión, sensibilidad y mAP no equivalen a porcentaje de cultivo protegido.
- 41 cruces registrados no constituyen una exactitud de conteo de 100 %.
- 120 épocas configuradas no equivalen a 120 ejecutadas; la corrida seleccionada registra 86.
- La prueba de Raspberry Pi excluyó cámara, interfaz y actuadores; no establece todavía latencia completa ni velocidad de trabajo.
- El texto propone validaciones futuras en tiempo futuro y conserva los resultados históricos como antecedentes preliminares.


## Actualización con el protocolo escrito

Se contrastó Protocolo_lumat.pdf, de 15 páginas, con el borrador. La instrucción actual del usuario prevalece sobre el objetivo histórico de detectar maleza. El título, la pregunta, la hipótesis, el objetivo general y la salida hacia actuadores ahora explicitan la detección del agave para evitar corte o daño durante el deshierbe autónomo.

El protocolo escrito delimita expresamente que no se incluye diseño, fabricación ni validación mecánica completa del equipo (página impresa 10, página 11 del PDF). Se conserva esa delimitación y se precisa el módulo de percepción y salida; no se añade navegación autónoma como compromiso nuevo. Se incorporó la relación de la metodología con las cuatro fases originales y las alternativas de comunicación GPIO/UART/serial, sujetas al controlador disponible.

La hipótesis ya no exige superar un algoritmo por color: su criterio central es detectar y proteger oportunamente el agave. La comparación básica queda opcional. Se añadió cómo distinguir señales de protección de los cortes o daños observados en eventuales pruebas integradas.

Se recuperó de la bibliografía original Flores et al. (2021), DOI 10.3390/drones5010004, referencia [17]. Sus metadatos y resumen se comprobaron en el registro del editor en Crossref. El texto original del estado del arte lo ubicaba en 2023, pero la referencia y el registro bibliográfico corresponden a 2021. Se incluye el protocolo como fuente interna [18].

El protocolo declara Raspberry Pi 3 Modelo B+ y YOLOv8; los avances posteriores documentan YOLO26s y una prueba en Raspberry Pi 4 de 2 GB. No se fusionan esas configuraciones como si fueran el mismo experimento. La cámara del protocolo es Hikvision; el despliegue posterior menciona Dahua. El borrador mantiene cámara RGB como categoría funcional hasta fijar la configuración final.

El protocolo completo permite recuperar también el enlace de Control de malezas en agave azul 1ª parte: https://eldespertardelcampo.com.mx/2023/02/28/control-de-malezas-en-agave-azul-1a-parte/ . Se conserva como fuente de divulgación disponible, sin incorporar afirmaciones nuevas sin revisión de su contenido.

Las referencias restantes del protocolo no se trasladan automáticamente: permanecen disponibles para ampliar antecedentes sobre detección de maleza, pero no son necesarias para justificar cada decisión de protección del agave. La revisión no modifica el PDF original del protocolo.
