# Respaldo de video de campo

Esta carpeta contiene el grabador. Antes del primer uso, instalar FFmpeg local como se indica en [la guia de hardware](../README.md). Usa Python en Windows; despues de preparar las dependencias no necesita Raspberry, SSH, internet ni instalar paquetes en campo. Las credenciales se crean localmente y estan cifradas para el usuario de Windows. Cada computadora necesita introducir sus propias credenciales de la CAMARA; este repositorio no las contiene.

## Preparar una vez, antes de salir

Con la laptop y la camara en el mismo router, abrir PowerShell desde la raiz del repositorio:

```powershell
cd hardware/camera
powershell -ExecutionPolicy Bypass -File .\Preparar-Camara.ps1 -IP 192.168.1.134
```

Usar la IP actual de la camara si cambio. El comando consulta y respalda su configuracion de red y pide escribir FIJA para conservar esa IP y desactivar DHCP. Esto permite arrancar sin servidor DHCP, incluso despues de apagar la camara. En un router debe reservarse esa IP para evitar que se asigne a otro dispositivo. Si el firmware no permite verificar el cambio, hacerlo en la interfaz web de la camara y probar el enlace directo antes de salir.

## En campo: laptop conectada directamente a la camara

La camara necesita su alimentacion propia o un inyector PoE adecuado. Conectar Ethernet directamente a la laptop. Abrir **PowerShell como administrador** desde la raiz del repositorio y ejecutar:

```powershell
cd hardware/camera
powershell -ExecutionPolicy Bypass -File .\Red-Directa.ps1
powershell -ExecutionPolicy Bypass -File .\Grabar.ps1 -IP 192.168.1.134
```

Red-Directa configura solo Ethernet y guarda su configuracion anterior. No ejecutarlo con Ethernet conectado al router. Si el adaptador tiene otro nombre, pasar `-Adaptador 'nombre'`. Las redes cubiertas son 192.168.1.x, 192.168.0.x y 10.1.1.x. La laptop usa la direccion .240, que no debe ser la IP de la camara. No proporciona DHCP.

Sin `-IP`, el grabador prueba las direcciones conocidas y busca RTSP en esas tres redes; pide elegir si encuentra otros equipos.

**Presionar ENTER para detener**, manteniendo el cable conectado hasta que termine. No cerrar la ventana ni suspender la laptop durante la grabacion.

Los archivos quedan en `hardware/camera/videos/fecha_hora/`, fuera del seguimiento de Git. Se guarda el flujo principal original, sin audio, sin modelo y sin recodificar, en segmentos MKV de unos cinco minutos (segun los fotogramas clave). Para leerlos puede usarse VLC. La ventana informa los megabytes escritos. Reintenta conexiones caidas; detiene la grabacion si queda menos de 1 GB libre. Comprobar un archivo reproducible antes de iniciar la toma de campo.

## Grabacion interna de la camara

Si la API confirma almacenamiento escribible, guarda el modo anterior y solicita grabacion manual. Que acepte la orden no prueba que haya generado archivos: hay que revisar la reproduccion/archivos en la camara. Si no puede confirmar almacenamiento o la orden falla, continua grabando en la laptop. No formatea ni borra la memoria; se aplica la politica de espacio/sobrescritura que ya tenga la camara.

Al detener, restaura el modo anterior. Si se pierde la conexion o se cierra abruptamente, reconectar y ejecutar:

```powershell
powershell -ExecutionPolicy Bypass -File .\Restaurar-Camara.ps1
```

## Volver a usar el router

En PowerShell como administrador, antes de reconectar Ethernet al router:

```powershell
powershell -ExecutionPolicy Bypass -File .\Red-Directa.ps1 -Restaurar
```

## Validacion

Las secciones siguientes conservan el registro de las pruebas de octubre de 2026 en la computadora original. Los videos y el estado de red de aquella prueba permanecen en su respaldo local; no se incluyen al clonar este repositorio.

Scripts Python/PowerShell revisados sintacticamente y FFmpeg disponible localmente. La prueba de video con la camara real y su memoria interna queda pendiente porque no fue accesible desde la laptop durante la preparacion. La configuracion Ethernet directa no se ha aplicado a la laptop durante esta preparacion, para mantener su conexion actual.

Referencia de los comandos de almacenamiento y RecordMode (0 automatico, 1 manual, 2 detenido): documento Dahua HTTP API for IPC V1.67, secciones 8.1 y 10.2: https://gizmoware.net/easyptz/DAHUA_HTTP_API_FOR_IPC%20V1.67.pdf

## Prueba real del 9 de octubre de 2026

Camara conectada directamente al Ethernet de la laptop: encontrada en 192.168.1.134. Se grabo un archivo real de 19.531 segundos, 293 cuadros, HEVC 2880x1620 a 15 fps. FFmpeg lo decodifico completo sin errores. Archivo: videos/2026-10-09_18-50-02/toma_001_0000.mkv. La prueba anterior pendiente queda resuelta para grabacion local.

La interfaz HTTP de la camara en puerto 80 acepta conexion pero no responde solicitudes; no se pudo verificar memoria interna ni configurar IP fija. NO se ha comprobado que conserve direccion despues de apagarla. Antes de salir conviene probar apagado/encendido con conexion directa; si necesita DHCP habra que fijar su IP al recuperar acceso a configuracion.

Ethernet tiene prioridad sobre Wi-Fi para las redes locales de la camara. El comando Grabar sin -IP prueba primero .134 y luego busca si cambio. Se dejo Ethernet configurado para conexion directa; restaurarlo antes de volver al router.
