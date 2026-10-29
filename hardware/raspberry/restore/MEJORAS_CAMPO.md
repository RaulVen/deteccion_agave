# Arranque local y video fluido — 2026-10-09

## Resultado comprobado

El visor arrancó, encontró la cámara en 192.168.1.107 y ejecutó detección
con el acceso a internet bloqueado mediante un servicio temporal de systemd:
IPAddressDeny=0.0.0.0/0 y ::/0; se permitieron solo 192.168.1.0/24 y loopback.
Se comprobó acceso al puerto 554 de la cámara y falta de acceso a 1.1.1.1:443
bajo esa política. Se mantuvo la red local actual: no se desconectó el router.

Muestra final con esa restricción, después del arranque:

- Captura: 15.61 cuadros/s (estimación sobre unos 10 segundos).
- Presentación en pantalla: 15.01 cuadros/s.
- Detección: 1.29 inferencias/s; última inferencia 0.784 s.
- Antigüedad del último cuadro recibido por el proceso: 0.136 s.
  Esto NO mide el retraso completo desde el sensor de la cámara.
- El equipo reportó bajo voltaje y throttling activos (0x50005).
  La alimentación debe corregirse para una comparación estable de rendimiento.

## Cambios

- La búsqueda prueba primero la IP guardada de la última cámara y luego las
  direcciones preferidas; solo escanea la subred si hace falta. La cámara actual
  se encontró en aproximadamente 2–3 segundos.
- Se eliminó el intento a ciegas contra una IP de respaldo no verificada.
- Iniciar Agave muestra un terminal durante la búsqueda y mensajes de fallo.
- Se desactivaron comprobaciones online e instalaciones automáticas de YOLO.
- Captura RTSP en un hilo que consume continuamente el stream, conservando el
  último cuadro, sin una cola creciente de video para mostrar.
- Inferencia en un proceso separado para que NCNN no bloquee el intérprete del
  visor. Colas acotadas; no se intenta inferir todo el video atrasado.
- Dibujo mediante SDL/Pygame con aceleración gráfica, escalando en GPU desde la
  resolución de cámara a la pantalla. Límite de presentación: 15 cuadros/s.
- Línea roja movible, persistencia, X de salida y accesos conservados.
  Mover la línea borra asociaciones previas para evitar cruces falsos al calibrar.
- Los procesos se agrupan para detener captura, visor e inferencia juntos.
- Se corrigió una redirección de Bash: "$12" estaba enviando el registro al
  archivo python2 del entorno; ahora se usa "${12}" y el registro correcto.

## Modelo y equivalencia

Se conserva el best.pt original, con SHA256
A847C3E25D4AF7B6AC8B78033F5A268034D67B621DFBCB61456BA33E454F2C0A.

El predeterminado ahora es su exportación NCNN FP32, entrada 320×320, en
/home/bioiot/deteccion_agave/best_ncnn_model. No se reentrenó.
El exportador de Ultralytics deshabilitó la rama end-to-end para NCNN;
esta versión usa NMS y sus resultados no son idénticos a los del .pt.

En las mismas diez imágenes de test, confianza 0.20 e IoU de matching 0.50:

| Backend | TP | FP | FN | Precisión | Recall |
|---|---:|---:|---:|---:|---:|
| PyTorch original | 52 | 32 | 70 | 0.619 | 0.426 |
| NCNN exportado | 56 | 22 | 66 | 0.718 | 0.459 |

Es una comprobación pequeña a umbral fijo, no mAP ni una validación completa.
Los tamaños de entrada efectivos también pueden diferir: PyTorch permite
padding rectangular, mientras el exportado tiene entrada cuadrada fija.

Se verificó además el motor NCNN directo contra Ultralytics+NCNN en las diez
imágenes: mismo número de detecciones en todas y diferencia numérica máxima
menor que 0.0002 en las coordenadas/puntuaciones comparadas.

El motor directo evita cargar PyTorch/Ultralytics para la ejecución normal y
usa dos hilos para reservar CPU al video. En esta copia de Git se conservan
los parámetros, metadatos y hashes en [best_ncnn_model](best_ncnn_model/README.md).
El binario de pesos permanece en el respaldo local y debe transferirse aparte.

Las mediciones aisladas fueron 2.77 s/imagen con PyTorch y 0.51 con Ultralytics
NCNN; el motor directo con dos hilos midió 0.70 s. Hubo alimentación inestable:
estas cifras NO son una comparación controlada a frecuencia constante.
El rendimiento del sistema completo se reporta por separado arriba.

## Uso y pendiente de red

Los accesos del escritorio se comprobaron mediante gio launch: Detener Agave
eliminó el PID del visor y su grupo, e Iniciar Agave volvió a encontrar la cámara
y a ejecutar el sistema. Se dejó el visor iniciado para las pruebas del usuario.
En una muestra posterior al retirar el bloqueo de internet, el video mantuvo
15.03 FPS y la detección llegó a 2.39 inferencias/s (última inferencia 0.36 s).
El bajo voltaje ya no estaba activo en la siguiente consulta (0x50000, histórico).
No atribuir esta diferencia a internet: coincidió con cambios de alimentación/
limitación de CPU; NCNN directo no consulta internet durante la inferencia.

El programa y el modelo no necesitan internet para funcionar. Sí necesitan una
red local entre cámara y Raspberry. La Raspberry continúa con DHCP en eth0;
no se modificó la red activa ni la configuración de la cámara.

Está pendiente confirmar si en campo se usará un router local o conexión
Ethernet directa. En conexión directa sin DHCP deben configurarse direcciones
estáticas en ambos extremos. La prueba de internet bloqueado no demuestra
funcionamiento tras retirar el router.

La alimentación presentó bajo voltaje repetido. La fluidez del video no equivale
a detección a 15 FPS: el detector ejecuta aproximadamente 1.3 inferencias/s en
la prueba completa, y no se ha validado el conteo desde un vehículo en marcha.

## Rutas

- Programa: /home/bioiot/deteccion_agave/scripts/
- Configuración privada: /home/bioiot/.config/agave-display.env
- Selección del modelo: AGAVE_MODEL_PATH en esa configuración.
- Posición de línea: rpi_live_tests/line_ratio.txt dentro del proyecto.
- Métricas: rpi_live_tests/performance.json y live_display.log.
- Respaldo anterior: backup_before_offline_20261009 dentro del proyecto.
- Configuración anterior: ~/.config/agave-display.env.before_offline.
- Entorno reutilizado: /home/bioiot/agave_benchmark_20260921/venv.

Se instalaron NCNN y las herramientas de conversión mientras había conexión;
la conversión no se repite al iniciar en campo. Pygame ya estaba instalado.
