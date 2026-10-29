# Cámara conectada directamente por Ethernet

Actualización: 9 de octubre de 2026.

## Uso

1. Encender la Raspberry y alimentar la cámara con su fuente o sistema PoE.
2. Conectar el cable de red de la cámara al Ethernet de la Raspberry.
3. Abrir **Iniciar Agave** en el escritorio.
4. Esperar la preparación de red y la búsqueda. Si la cámara está arrancando,
   el programa reintenta hasta seis veces; permitir unos dos minutos.

El terminal debe indicar **Modo campo listo** antes de buscar la cámara.
La Raspberry usa 192.168.1.239/24 y ofrece DHCP local entre 192.168.1.100 y
192.168.1.150 a las cámaras que solicitan una dirección. Una cámara que conserve
su IP fija puede encontrarse sin pedir DHCP.

Busca primero la última IP encontrada y las preferidas, después todas las
direcciones de 192.168.1.0/24, 192.168.0.0/24 y 10.1.1.0/24. No busca todo IPv4.
Para las dos subredes adicionales agrega direcciones locales .239 en Ethernet.
El modelo, el video y esta red local no requieren router ni internet.

## Comportamiento en el laboratorio

Antes de cambiar Ethernet se comprueba mediante ARP el router local conocido
(192.168.1.254, o la puerta de enlace actual de eth0). Si responde, se conserva
la red de laboratorio y no se activa el servidor DHCP de campo.

## Implementación y comprobaciones

- Perfil NetworkManager: **Agave campo directo**, método IPv4 shared,
  IPv6 desactivado, sin ruta predeterminada, autoconexión desactivada.
  El botón activa el perfil solo cuando no encuentra el router local.
- Preparación: /usr/local/sbin/agave-field-network, propiedad de root.
- Permiso limitado: /etc/sudoers.d/agave-field-network permite a bioiot ejecutar
  únicamente ese programa, sin argumentos y sin pedir contraseña.
- Estado: /run/agave-field-network.json.
- Se verificaron sintaxis, permisos sudo y el comportamiento conservador al
  detectar el router actual.
- Se clonó temporalmente el perfil sobre un par Ethernet virtual aislado,
  con un cliente en un namespace sin router. El cliente completó DHCP
  DISCOVER/OFFER/REQUEST/ACK y recibió 192.168.77.119 del servidor 192.168.77.239.
  Se eliminaron perfil e interfaces de prueba al terminar.
- La conexión física cámara–Raspberry requiere la comprobación del usuario:
  cambiar el cable corta el SSH actual y el Wi-Fi guardado no está disponible.
  No se debe confundir la prueba virtual de DHCP con la validación de su cámara.

El arranque sigue usando NCNN local y el visor con aceleración gráfica, línea
roja movible y accesos de iniciar/detener de la versión anterior.
