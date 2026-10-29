# Prueba de YOLO26s en Raspberry Pi 4 de 2 GB

Fecha: 21 de septiembre de 2026.

## Resultado

El modelo original carga y ejecuta inferencias correctamente en esta Raspberry.
La memoria resultó suficiente en la prueba aislada. El principal límite observado
es la velocidad: aproximadamente una imagen procesada por segundo.

| Medición | Resultado |
|---|---:|
| Inferencias medidas, excluyendo 3 de calentamiento | 60 |
| Imágenes diferentes del conjunto de prueba | 10 |
| Tiempo medio de predict, incluido pre/postprocesamiento | 1.0657 s |
| Mediana | 1.0668 s |
| Mínimo / máximo | 1.0544 / 1.0973 s |
| Rendimiento de predict | 0.9384 imágenes/s |
| Pico de RAM del proceso, RSS | 482.00 MiB |
| Mínima RAM disponible del sistema | 1190.34 MiB |
| Máximo uso de swap observado | 0 MiB |
| Máxima temperatura registrada | 74.984 °C |
| Indicadores de limitación / bajo voltaje al finalizar | 0x0 |
| Duración total del proceso, incluidas importaciones y lecturas | 125.69 s |

La carga del objeto YOLO tardó 0.47 s después de importar las bibliotecas.
La primera llamada a predict tardó 7.08 s, incluido su arranque interno;
no está incluida en el promedio. No interpretar los 0.47 s como el tiempo
total necesario para arrancar la aplicación desde el escritorio.

## Condiciones y reproducibilidad

- Equipo: Raspberry Pi 4 Model B Rev 1.5, 2 GB, Debian 13, ARM64.
- Modelo: yolo26s_sgd_cos_slow_120e/weights/best.pt, 20,292,037 bytes.
- SHA256 comprobado también en la Raspberry:
  A847C3E25D4AF7B6AC8B78033F5A268034D67B621DFBCB61456BA33E454F2C0A.
- PyTorch 2.6.0+debian, Ultralytics 8.4.90, OpenCV 4.10.0.
- CPU, imgsz=320, conf=0.20, iou=0.40, lote de una imagen.
- Diez imágenes distribuidas en la lista ordenada de 36 imágenes de test.
  Las rutas originales están en input_manifest.json.
- Cada imagen se redujo a 640×360 sin recorte, como el substream documentado.
- El tiempo medido comienza después de leer y reducir la imagen. Incluye
  el preprocesamiento de Ultralytics, la red y el postprocesamiento.
- Se solicitaron 4 hilos al inicio, pero Ultralytics reajustó PyTorch a 3;
  el resultado registra ambos valores. No es una comparación entre 3 y 4 hilos.
- Se monitorizó RAM, swap y temperatura aproximadamente cada 0.2 segundos.
  El pico RSS proviene además de getrusage, no solo del muestreo.
- No hubo cámara RTSP, dibujo de interfaz ni conteo por cruce en esta prueba.
- Se observaron detecciones de la clase agave. Esto no mide precisión ni recall.
- La prueba de unos dos minutos no garantiza estabilidad térmica durante
  horas de operación en campo.

## Interpretación y siguiente paso

Puede usarse para pruebas de detección con este mismo modelo. La RAM observada
deja margen para añadir componentes, pero el sistema completo debe medirse.
Con aproximadamente una inferencia por segundo, el conteo de plantas que pasan
rápidamente por una línea puede omitir cruces o perder correspondencias.
No se puede certificar una velocidad de avance sin un video representativo.

Conviene conservar este modelo como referencia y comparar una versión optimizada
para CPU antes de cambiar el entrenamiento o comprar otro equipo. También se debe
comprobar la refrigeración bajo una prueba más prolongada: llegó a 75 °C aunque
no hubo limitación de frecuencia durante esta medición.

## Archivos y cambios realizados

En la Raspberry: /home/bioiot/agave_benchmark_20260921/

- best.pt: copia verificada del modelo original.
- images/: diez imágenes de prueba.
- benchmark.py: programa de medición.
- venv/: entorno aislado con acceso a las bibliotecas de Debian.
- wheels/: paquetes descargados para reproducir la instalación.
- results_threads4.json: mediciones y muestras de recursos.
- benchmark_threads4.log: salida completa.

Se instalaron bibliotecas de inferencia de Debian y sus dependencias (APT estimó
1,254 MB adicionales), y Ultralytics 8.4.90 con sus paquetes complementarios en
el entorno aislado. No se reinstaló todavía la aplicación de campo.

Repetición en la Raspberry:

```bash
cd /home/bioiot/agave_benchmark_20260921
venv/bin/python -u benchmark.py --threads 4 --count 60 --output results_repeat.json
```

Se descargaron a este directorio local el JSON y el registro completo.
remote.py recibe la contraseña mediante RPI_PASSWORD; no la guarda en el archivo.
