# Restauración del visor de agaves — 2026-10-09

Instalado en /home/bioiot/deteccion_agave en pa-bioiot (192.168.1.95).
Cámara encontrada automáticamente en 192.168.1.107.

Se restauraron los scripts del bundle agave_rpi_usb_bundle_20260813-231735,
la configuración privada de cámara y los accesos Iniciar Agave y Detener Agave.
El modelo se copió desde la prueba anterior y su SHA256 se verificó:
A847C3E25D4AF7B6AC8B78033F5A268034D67B621DFBCB61456BA33E454F2C0A.

Se reutilizó el entorno /home/bioiot/agave_benchmark_20260921/venv mediante
el enlace .venv-rpi-apt. Debe conservarse ese entorno para ejecutar el visor.

Cambios sobre el bundle: línea y marcador en rojo; detección de resolución del
monitor con wlr-randr (monitor actual 1920×1080); OpenCV limitado a un hilo;
arranque en segundo plano con entradas/salidas independientes de SSH; parada
del proceso hijo al volver a iniciar; errores de apertura sin exponer URL RTSP.

Verificado: hash del modelo, sintaxis Python/Bash, búsqueda automática de cámara,
video e inferencia en pantalla completa, parada y reinicio por los scripts de los
accesos, persistencia de line_ratio.txt (0.6597 al verificar). Captura: restored.png.
No se verificó precisión del conteo con plantas en movimiento: la cámara muestra
una habitación sin agaves. El visor quedó ejecutándose.

Mouse: clic o arrastre mueve la línea; clic derecho la centra; rueda ajusta;
X roja sale. Se guarda la posición en rpi_live_tests/line_ratio.txt y los eventos
de cruce en rpi_live_tests/detections.jsonl.

Se observó un aviso de bajo voltaje en el escritorio y throttled=0x50000:
historial de bajo voltaje y throttling desde el arranque, sin esos bits activos
en la consulta puntual. Revisar alimentación antes de evaluar rendimiento.
