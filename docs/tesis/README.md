# Redacción de la tesis

Esta es la carpeta de trabajo para redactar desde cualquiera de las dos computadoras. Los archivos Markdown (`.md`) son las fuentes editables; los PDF son exportaciones para lectura y revisión. Las copias originales en la carpeta local `ChatGPT/tesis` se conservaron, pero los cambios que se quieran sincronizar deben hacerse en este repositorio.

## Por dónde continuar

Si vienes de la otra computadora o abres un chat nuevo, empieza por [el contexto del chat de redacción](CONTEXTO_CHAT_REDACCION.md). Resume las decisiones, el estilo solicitado y el estado de cada versión.

| Archivo o carpeta | Uso |
|---|---|
| [Capítulo 1 del autor](insumos_usuario/Tesis_Lumat_Cap1.pdf) | PDF que se revisó el 27 de octubre; referencia del texto y tono del autor |
| [Protocolo original](insumos_usuario/Protocolo_lumat.pdf) | Antecedente de estructura y referencias; su enfoque anterior debe interpretarse según el contexto del chat |
| [Capítulo 2 ampliado](Capitulo_2_Marco_teorico_ampliado.md) | Borrador más reciente del capítulo 2, actualizado el 28 de octubre de 2026; empezar aquí para continuar este capítulo |
| [PDF del capítulo 2 ampliado](Capitulo_2_Marco_teorico_ampliado.pdf) | Exportación existente de ese borrador |
| [Capítulo 1 y marco teórico](Capitulo_1_y_marco_teorico_agave.md) | Borrador previo del 5 de octubre; incluye una versión anterior del capítulo 2 |
| [Revisión del capítulo 1](Revision_capitulo_1_2026-10-27.md) | Observaciones del 27 de octubre para orientar la revisión del capítulo 1 |
| [Contexto del proyecto](Contexto_del_proyecto_para_redaccion_2026-10-27.md) | Estado computacional y evidencia para escribir metodología y resultados |
| [Capítulo 2 del 27 de octubre](Capitulo_2_Marco_teorico_2026-10-27.md) | Borrador anterior, conservado como referencia; no es la versión ampliada |
| [Notas y fuentes previas](Notas_de_revision_y_fuentes.md) | Notas que acompañaban al borrador de octubre 5 |
| [Notas de revisión](notas/) | Auditorías de modelos, bibliografía, sistema embebido, aumentos y métricas; propuestas de redacción |
| [Protocolo previo](historico/protocolo_previo/) | Copia histórica anterior al borrador del 5 de octubre |
| [Figuras del capítulo 2](figuras_capitulo2/) | Imágenes que usa el Markdown ampliado |

Los documentos siguen siendo borradores: no se eligió una versión final ni se fusionaron capítulos. Al integrarlos hay que unificar la bibliografía, resolver referencias duplicadas y evitar incorporar dos versiones del capítulo 2.

Los [reportes Word](../reportes/), el [artículo](../paper/) y la [evidencia computacional](../resultados/) mantienen sus carpetas propias. No hace falta entrenar modelos ni instalar el entorno de GPU para editar estos textos o consultar sus PDF.

## Flujo entre computadoras

1. Antes de empezar, desde la raíz del repositorio, ejecutar `git status` y `git pull --ff-only origin main`. Si quedan cambios propios sin guardar, hacer su commit antes de traer cambios. Si Git informa divergencias, resolverlas antes de editar.
2. En la computadora de redacción, trabajar principalmente en `docs/tesis/`, `docs/paper/` y `docs/reportes/`. Editar el Markdown como fuente y mantener los enlaces a figuras relativos.
3. En la computadora de cálculo, mantener código y experimentos en sus carpetas actuales y actualizar los reportes y resúmenes compartidos cuando haya resultados nuevos.
4. Antes de cambiar de computadora, revisar `git diff`, añadir solo los archivos intencionados, hacer commit y `git push origin main`. En la siguiente computadora, descargar esos cambios antes de continuar.

Conviene terminar y subir una sesión antes de abrir los mismos archivos en la otra computadora. Los PDF, Word e imágenes no se fusionan automáticamente como el texto; sus cambios simultáneos se resuelven eligiendo una versión o regenerando la exportación desde la fuente revisada.

## Exportar PDF cuando haga falta

Los PDF existentes se incorporaron sin regenerarlos. Los tres exportadores leen el Markdown actual y nunca lo sustituyen por texto incluido dentro del programa. Para usarlos basta un entorno Python con las dependencias de [requirements.txt](../../scripts/redaccion/requirements.txt):

```powershell
python -m venv .venv-redaccion
.\.venv-redaccion\Scripts\python.exe -m pip install -r scripts/redaccion/requirements.txt
.\.venv-redaccion\Scripts\python.exe scripts/redaccion/crear_capitulo2_ampliado.py --overwrite
```

Los scripts resuelven los documentos respecto a la raíz del repositorio, aunque se ejecuten desde otra carpeta. `--overwrite` permite reemplazar el PDF existente; sin esa opción el exportador se detiene. Los otros exportadores son [crear_pdf.py](../../scripts/redaccion/crear_pdf.py), para el borrador conjunto de capítulo 1 y marco teórico, y [crear_capitulo2.py](../../scripts/redaccion/crear_capitulo2.py), para el borrador del 27 de octubre. Se puede consultar cada comando con `--help`.

El exportador ampliado usa las imágenes enlazadas desde el Markdown. Solo `--regenerate-figures` reemplaza las dos figuras con los diagramas definidos en el script; requiere `pdftoppm` de Poppler disponible en `PATH`, o una ruta configurada mediante la variable de entorno `PDFTOPPM`. No hace falta Poppler para exportar con las imágenes que ya están en el repositorio.

Los exportadores buscan Times New Roman y, si no está disponible, Liberation Serif o DejaVu Serif en ubicaciones habituales de Windows, macOS y Linux. También se puede indicar una carpeta mediante `THESIS_FONT_DIR`. La tipografía elegida puede cambiar la paginación: revisar visualmente el PDF después de exportar y subirlo junto con el Markdown que lo produjo. Las fechas impresas en las plantillas de los exportadores identifican los borradores originales.

El script [ordenar_referencias_ampliado.py](../../scripts/redaccion/ordenar_referencias_ampliado.py) solo muestra el orden propuesto al ejecutarlo sin opciones. `--apply` modifica la numeración en el Markdown actual y guarda una copia previa en `tmp/redaccion/`; usarlo después de revisar la bibliografía. No inserta redacción nueva.

## Insumos que permanecen locales

Git comparte las fuentes, figuras, PDF, reportes y resúmenes incluidos en el repositorio. Las imágenes y etiquetas completas del dataset, videos, pesos, checkpoints, entornos Python y archivos temporales permanecen en la computadora de cálculo; no son necesarios para redactar. Los manifiestos y resúmenes pequeños permiten consultar procedencia y resultados sin descargar esos archivos grandes.

Las auditorías en `notas/` conservan las rutas originales que citaban como evidencia de la revisión. Una ruta a `.venv`, `runs/`, `video_predictions/`, `backups/` o a carpetas externas puede referirse a un insumo local que no estará en la otra computadora. El [contexto del proyecto](Contexto_del_proyecto_para_redaccion_2026-10-27.md) enlaza los resúmenes compartidos de conteos y Raspberry.

Las imágenes de inspección de páginas y extracciones de texto de `tmp/revision*` no se copiaron. Sí se conservaron las notas de investigación, las fuentes de los capítulos y el protocolo previo. Los nuevos archivos temporales o respaldos de los scripts se guardan en `tmp/redaccion/`.
