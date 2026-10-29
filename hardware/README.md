# Cámara y Raspberry Pi

Esta carpeta reúne las copias de trabajo de cámara, benchmark y visor Raspberry que antes estaban separadas del repositorio. Los respaldos originales permanecen en la computadora de trabajo computacional. Se sincronizan fuentes, instrucciones y resultados pequeños para que puedan consultarse también durante la redacción de la tesis.

| Carpeta | Contenido |
|---|---|
| [camera](camera/LEEME.md) | Grabación del video original de una cámara Dahua desde Windows. |
| [raspberry/benchmark](raspberry/benchmark/RESULTADO.md) | Benchmark de inferencia CPU, manifiesto de imágenes y resultados históricos. |
| [raspberry/health_monitor](raspberry/health_monitor/rpi_health_monitor.py) | Monitor local de la Raspberry mediante SSH. |
| [raspberry/restore](raspberry/restore/README.md) | Respaldo de scripts y documentación de la instalación de campo. |

## Grabador en Windows

Requiere Python 3.12, PowerShell, conexión Ethernet con la cámara y FFmpeg local. Preparar las dependencias con internet antes de salir a campo. Desde la raíz del repositorio:

```powershell
python -m pip install --target hardware/camera/vendor imageio-ffmpeg==0.6.0
cd hardware/camera
powershell -ExecutionPolicy Bypass -File ./Grabar.ps1 -IP 192.168.1.134
```

La IP es la usada en la prueba histórica; indicar la dirección de la cámara actual. Seguir [LEEME.md](camera/LEEME.md) para preparar o restaurar Ethernet. Esos cambios de red requieren una consola con permisos de administrador. El grabador pide las credenciales la primera vez y crea `credentials.dpapi`, cifrado para el usuario de Windows de esa computadora.

`vendor/`, videos, credenciales, configuración anterior de Ethernet y estados de restauración son locales. No copiarlos entre computadoras mediante Git. Cada equipo debe generar su propio estado de red. Los scripts encuentran sus recursos junto a su propio archivo, sin depender de la carpeta de usuario.

## Monitor SSH

El monitor y `raspberry/benchmark/remote.py` requieren Paramiko instalado en el Python que los ejecute:

```powershell
python -m pip install paramiko
python hardware/raspberry/health_monitor/rpi_health_monitor.py --host DIRECCION_DE_LA_RASPBERRY --user USUARIO
```

El monitor solicita la contraseña si no existe la variable de entorno `RPI_PASSWORD`; muestra el panel en `http://127.0.0.1:8766`. El helper `remote.py` requiere esa variable y conserva el destino histórico `pa-bioiot`, usuario `bioiot`; revisar esos datos antes de usarlo en otra instalación. No necesita la antigua carpeta temporal de bibliotecas.

## Benchmark y visor en Raspberry

Los scripts de benchmark se ejecutan en Linux/Raspberry, no en Windows: usan `vcgencmd`, sensores de temperatura del sistema y el módulo `resource`. El entorno histórico contiene OpenCV, PyTorch, Ultralytics y psutil; las versiones medidas están en [RESULTADO.md](raspberry/benchmark/RESULTADO.md) y en el JSON de resultados.

`benchmark.py` espera `best.pt` y una carpeta `images/` junto a él. Esos datos no se incluyen aquí. Su hash de modelo está fijado para reproducir la prueba original; `input_manifest.json` enumera las diez imágenes mediante rutas relativas a la raíz del repositorio. Preparar las imágenes y los pesos antes de repetir el benchmark. Los logs completos permanecen en el respaldo local; el JSON conserva las mediciones.

El visor de campo utiliza NCNN, NumPy, PyYAML, OpenCV, Pygame/SDL, FFmpeg, una sesión gráfica Wayland y herramientas Linux de red. Los scripts conservan las rutas históricas de instalación `/home/bioiot/deteccion_agave`, el subdirectorio `scripts/`, el entorno `.venv-rpi-apt` y el archivo privado `~/.config/agave-display.env`. Clonar este repositorio no instala ni configura automáticamente la Raspberry. Consultar [la guía del respaldo](raspberry/restore/README.md) antes de desplegarlo.

## Archivos grandes y privados

Los pesos `.pt` y `model.ncnn.bin`, datasets, videos, dependencias descargadas, logs, capturas históricas y credenciales se conservan fuera de Git. El modelo NCNN tiene [metadatos y hashes](raspberry/restore/best_ncnn_model/README.md) para identificar la copia correcta. Los informes históricos describen pruebas anteriores y no equivalen a una validación del hardware al clonar el proyecto en otra computadora.
