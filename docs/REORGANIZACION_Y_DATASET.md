# Reorganizacion e integracion del dataset — 2026-10-21

## Fuentes preservadas

- Base del benchmark: `datasets/yolo26/`, 404 imagenes, 4371 cajas; se conservan exactamente sus splits 295/73/36 y sus archivos.
- Exportacion nueva: `datasets/raw/maleza_2026-10-21/agave_maleza.yolo26.zip`, copia verificada del ZIP `agave maleza.yolo26.zip` de Descargas. 1826 imagenes y 10180 cajas; 47 etiquetas vacias corresponden a imagenes negativas incluidas en la exportacion.
- Roboflow: workspace `raul-stlme`, proyecto `agave-maleza`, version 1, clase `agave`; sin preprocesamiento ni aumentacion declarados en el README de exportacion.
- La exportacion contiene tres entradas `data.yaml` identicas. El preparador verifica su igualdad y conserva una copia de metadatos; las imagenes y etiquetas no estan duplicadas.

La integracion conserva 2230 imagenes y 14551 cajas en total, incluidas las reservas. Se copian los bytes originales de imagenes y etiquetas sin reescalado ni conversion de formato. Las imagenes nuevas reciben nombres estables por video y fotograma; el manifiesto enlaza cada una con su nombre Roboflow, clip de origen y archivo extraido.

## Particion reproducible

Se sustituye el split aleatorio de Roboflow (1279/364/183) por bloques temporales. El dataset antiguo conserva su division para mantener la trazabilidad del benchmark.

| Videos nuevos | Destino |
|---|---|
| v02-v07, v11-v16 | Entrenamiento |
| v08-v10 | Validacion |
| v17-v19 | Prueba |

Las colas de v07, v10 y v16, y los primeros 60 segundos de v08, v11 y v17, se guardan en reserva. No se usan para entrenar ni evaluar. En total: train 1493, val 435, test 136, reserva 166. Ningun clip nuevo reparte imagenes entre los tres conjuntos activos.

Se confirmo continuidad visual entre v03 y v04; ambos permanecen en train. v12-v15 incluyen grabaciones cuyos horarios se solapan y tambien quedan juntos. Los videos proceden de una misma salida y hay posibles revisitas: la separacion temporal reduce proximidad, no garantiza independencia espacial. Hace falta una captura de otro campo o fecha para medir generalizacion externa. El split historico puede tener correlacion temporal previa.

Las imagenes de la extraccion anterior que no aparecen en este ZIP no se agregaron ni se trataron como negativos: solo se usan las 1826 exportadas con sus etiquetas.

## Verificaciones

Se decodifican todas las imagenes y se comprueba su resolucion 2880x1620. Se valida correspondencia imagen/etiqueta, clase, cinco campos por caja, valores finitos y coordenadas normalizadas. Se calculan SHA-256 del archivo, los pixeles RGB y las etiquetas; no se encontraron imagenes exactamente duplicadas entre las fuentes.

Algunas cajas tocan el borde con un exceso inferior a una centesima de pixel debido al redondeo del export (193 cajas nuevas y 9 historicas). Se acepta una tolerancia normalizada de 0.00001 y se mantienen las etiquetas originales. Esto no representa cajas materialmente fuera de la imagen.

Los manifiestos y el informe resumen permiten verificar recuentos, procedencia, negativos y cajas por split. La validacion automatica de formato no sustituye una revision exhaustiva de la calidad del etiquetado manual.

Reproduccion, desde la raiz del repositorio y sobre una salida inexistente:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_combined_dataset.py --zip "datasets/raw/maleza_2026-10-21/agave_maleza.yolo26.zip" --extraction-manifest "C:/Users/iceve/Documents/videos/roboflow_maleza_2026-10-18/documentacion/manifiesto_final.json"
```

El script se niega a sobrescribir una version existente. La regla esta en `configs/datasets/agave_maleza_2026-10-21.json`; el `data.yaml` de salida usa una ruta absoluta para evitar la resolucion ambigua de Ultralytics. Si se traslada el repositorio a otra carpeta, actualizar ese campo `path` antes de entrenar.

## Orden del proyecto y preservacion

Se agruparon configuraciones en `configs/`, pesos base en `models/pretrained/`, reportes Word en `docs/reportes/`, evidencia en `docs/evidencia/` y articulo en `docs/paper/`. Se actualizaron las referencias ejecutables de los scripts y los enlaces de la documentacion.

`runs/`, `datasets/yolo26/`, `benchmark/agave_benchmark.csv` y `video_predictions/` conservan su ubicacion y contenido porque los reportes y checkpoints historicos dependen de esas rutas. Los YAML historicos se guardan como evidencia; para entrenar se usan los nuevos YAML mediante el ejecutor, que resuelve las rutas de los pesos.

`backups/reorganizacion_2026-10-21/` guarda 76 archivos previos (incluidos cambios locales), estado Git anterior, hashes y registro de movimientos. Se verifico por SHA-256 que los movimientos no alteraron contenidos. El README previo se conserva tambien en `docs/HISTORICO_BENCHMARK.md`, con sus referencias actualizadas. No se borraron los videos de campo ni se alteraron los resultados anteriores.


## Comprobacion final de uso

El ejecutor paso la comprobacion de datos, seis versiones de paquetes, importacion real de YOLO/Matplotlib y disponibilidad CUDA. Se cargo un lote de dos imagenes (una historica y una nueva) con Ultralytics y se completo una inferencia de los pesos base en la GPU RTX 5050, sin entrenamiento. El detalle queda en `docs/verificacion_preparacion_2026-10-21.json`.

En la primera importacion Windows Smart App Control bloqueo `matplotlib.ft2font`; se verifico que el binario coincide con el paquete oficial y el lock. Dos comprobaciones posteriores y la inferencia GPU pasaron sin reinstalar ni modificar politicas de seguridad. El incidente queda registrado; no se atribuye una reparacion permanente.

La [revision visual de etiquetas](dataset_2026-10-21/REVISION_ETIQUETAS.md) incluye una muestra de 12 imagenes y dos casos para revisar antes del entrenamiento. El dataset conserva las anotaciones originales.
