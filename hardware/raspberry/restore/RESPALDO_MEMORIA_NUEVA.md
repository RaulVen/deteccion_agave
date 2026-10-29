# Memoria de respaldo — 9 de octubre de 2026

Instalado en pa-bioiot, usuario bioiot, Debian 13. Sistema iniciado desde /dev/sda2, dispositivo 28.7 GiB; aproximadamente 20 GiB disponibles. El entorno /home/bioiot/deteccion_agave/.venv-rpi-apt es propio de esta memoria, sin enlace al entorno de la USB anterior.

Incluye el best.pt original con SHA256 A847C3E25D4AF7B6AC8B78033F5A268034D67B621DFBCB61456BA33E454F2C0A y el modelo NCNN optimizado que usa el visor. Ambos archivos NCNN coinciden con el respaldo local. Runtime: NCNN 1.0.20260526, OpenCV Debian 4.10, Pygame 2.6.1. El best.pt se conserva como original; el visor usa NCNN y no requiere PyTorch.

Accesos Iniciar Agave y Detener Agave instalados y probados. Visor en pantalla completa con linea roja movible, guardado de posicion y X para salir. La calibracion comienza centrada y debe ajustarse en campo. Se corrigio una carrera de arranque: espera que el proceso se independice antes de cerrar la terminal.

Modo Ethernet directo instalado: perfil Agave campo directo, DHCP local, direccion 192.168.1.239 y redes adicionales 192.168.0.x/10.1.1.x. Helper root y permiso sudo limitado verificados. Prueba DHCP aislada confirmo asignacion y ACK. No se cambio la conexion al router durante instalacion. La prueba fisica de cable directo en esta memoria queda pendiente.

Camara detectada en 192.168.1.107, video e inferencia comprobados. Visor aproximadamente 15 FPS; deteccion aproximadamente 2 FPS. Voltaje sin avisos activos ni historicos (get_throttled=0x0 durante prueba).

Para usar: apagar completamente la Raspberry antes de cambiar memorias; encender con esta memoria, conectar camara alimentada por Ethernet y abrir Iniciar Agave. Ajustar linea roja a la posicion necesaria.

Prueba sin internet: servicio temporal con IPAddressDeny=any, permitiendo solamente LAN y loopback. Video 14.97 FPS, deteccion 2.69 FPS, inferencia 0.358 s. Servicio temporal detenido despues; visor iniciado desde el acceso del escritorio.
