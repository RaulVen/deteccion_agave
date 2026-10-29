# Respaldo de la instalación Raspberry

Estos archivos corresponden al visor de campo y a las pruebas del 9 de octubre de 2026. Se preservan sus rutas remotas para documentar la instalación existente. Esta carpeta no es un instalador ni debe ejecutarse como si fuera la raíz del proyecto de la Raspberry.

Los lanzadores esperan los scripts en `/home/bioiot/deteccion_agave/scripts/`, un entorno Python en `.venv-rpi-apt`, el modelo configurado y el helper de red instalado en `/usr/local/sbin/agave-field-network`. `agave_start_display.new_memory.sh` conserva la variante de arranque para la memoria nueva, con espera a que el proceso se independice de la terminal; no sustituye automáticamente al otro lanzador.

La configuración privada se carga de `/home/bioiot/.config/agave-display.env`. Debe crearse localmente con `CAMERA_USER`, `CAMERA_PASSWORD` y, cuando corresponda, `AGAVE_MODEL_PATH`. Los demás ajustes opcionales se encuentran en los lanzadores. No incluir credenciales reales en archivos del repositorio. Los archivos de sudoers y de red son referencias de la instalación existente y requieren revisión de usuario, interfaz y rutas antes de instalarse en otro sistema.

El motor NCNN requiere `ncnn`, NumPy, PyYAML y OpenCV. El visor requiere además Pygame/SDL y una sesión gráfica; la búsqueda de cámara utiliza FFmpeg. La comparación con PyTorch utiliza Ultralytics y PyTorch. Las versiones y condiciones históricas están en los informes siguientes, incluyendo limitaciones por alimentación y tamaño de la muestra:

- [Restauración inicial](RESTAURACION.md).
- [Mejoras y equivalencia del modelo](MEJORAS_CAMPO.md).
- [Ethernet directo](ETHERNET_DIRECTO.md).
- [Memoria nueva](RESPALDO_MEMORIA_NUEVA.md).
- [Modelo NCNN y recuperación de pesos](best_ncnn_model/README.md).

Las capturas `.png`, el log completo y el binario NCNN permanecen en el respaldo original de esta computadora (`rpi_restore` dentro del espacio de trabajo anterior). Las menciones a esos archivos en los informes son evidencia histórica; no se incluyen en esta copia de Git. Los resultados JSON pequeños sí están presentes.
