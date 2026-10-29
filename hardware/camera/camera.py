"""Offline Dahua recorder. Secrets protected with Windows DPAPI for this user."""
import argparse, concurrent.futures, ctypes, datetime, getpass, ipaddress, json
import os, re, shutil, socket, subprocess, sys, time, urllib.request, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent

class Blob(ctypes.Structure):
    _fields_ = [('size', ctypes.c_ulong), ('data', ctypes.POINTER(ctypes.c_char))]

def protect(data, decrypt=False):
    buf = ctypes.create_string_buffer(data)
    src, dst = Blob(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_char))), Blob()
    fn = ctypes.windll.crypt32.CryptUnprotectData if decrypt else ctypes.windll.crypt32.CryptProtectData
    if not fn(ctypes.byref(src), None, None, None, None, 1, ctypes.byref(dst)):
        raise ctypes.WinError()
    try:
        return ctypes.string_at(dst.data, dst.size)
    finally:
        ctypes.windll.kernel32.LocalFree(dst.data)

def credentials():
    path = ROOT / 'credentials.dpapi'
    if not path.exists():
        value = {'user': input('Usuario camara: '), 'password': getpass.getpass('Clave camara: ')}
        path.write_bytes(protect(json.dumps(value).encode()))
    return json.loads(protect(path.read_bytes(), True))

def api(ip, cred, endpoint):
    base = 'http://' + ip
    manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    manager.add_password(None, base, cred['user'], cred['password'])
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPDigestAuthHandler(manager))
    return opener.open(base + '/cgi-bin/' + endpoint, timeout=8).read().decode('utf-8', 'replace')

def mode(ip, cred, value=None):
    if value is not None:
        result = api(ip, cred, 'configManager.cgi?action=setConfig&RecordMode[0].Mode=' + str(value))
        if result.strip() != 'OK':
            raise RuntimeError('La camara rechazo el modo de grabacion')
    text = api(ip, cred, 'configManager.cgi?action=getConfig&name=RecordMode')
    match = re.search(r'RecordMode\[0\]\.Mode=(\d+)', text)
    if not match:
        raise RuntimeError('No se pudo consultar el modo de grabacion')
    result = int(match[1])
    if value is not None and result != value:
        raise RuntimeError('La camara no confirmo el cambio')
    return result

def reachable(ip):
    try:
        with socket.create_connection((ip, 554), .3):
            return ip
    except OSError:
        return None

def find_camera(ip):
    if ip:
        return str(ipaddress.IPv4Address(ip))
    for host in ['192.168.1.134', '192.168.1.107', '192.168.1.108', '192.168.1.73']:
        if reachable(host):
            return host
    print('Buscando camara en las tres redes de campo...')
    for subnet in ['192.168.1.0/24', '192.168.0.0/24', '10.1.1.0/24']:
        with concurrent.futures.ThreadPoolExecutor(max_workers=64) as pool:
            hosts = list(pool.map(reachable, map(str, ipaddress.ip_network(subnet).hosts())))
        hosts = [host for host in hosts if host]
        if hosts:
            print('Equipos RTSP encontrados:', ', '.join(hosts))
            chosen = input('Escribe la IP de TU camara (Enter para cancelar): ').strip()
            if chosen in hosts:
                return chosen
            raise RuntimeError('Seleccion de camara cancelada')
    raise RuntimeError('No se encontro RTSP. Revisa alimentacion, cable e IP fija de la camara.')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--ip')
    p.add_argument('--seconds', type=int, default=0)
    p.add_argument('--inspect', action='store_true')
    p.add_argument('--restore-camera', action='store_true')
    p.add_argument('--fixed-camera', action='store_true')
    args = p.parse_args()
    cred = credentials()
    state = ROOT / 'camera_restore.json'
    if args.restore_camera:
        old = json.loads(state.read_text())
        mode(old['ip'], cred, old['mode'])
        state.unlink()
        print('Modo anterior de camara restaurado.')
        return
    ip = find_camera(args.ip)
    print('Camara:', ip)
    if args.fixed_camera:
        network = api(ip, cred, 'configManager.cgi?action=getConfig&name=Network')
        (ROOT / ('network_camera_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.txt')).write_text(network)
        print(network)
        match = re.search(r'table.Network\.([^\s.]+)\.IPAddress=' + re.escape(ip) + r'(?:\s|$)', network)
        if not match:
            raise RuntimeError('No se identifico la interfaz de la camara. No se hicieron cambios.')
        interface = match[1]
        if not re.search(r'table.Network\.' + re.escape(interface) + r'\.DhcpEnable=(true|false)', network):
            raise RuntimeError('El firmware no expone DHCP con el formato esperado.')
        print('Se conservara la IP actual y se desactivara DHCP para usar cable directo.')
        if input('Escribe FIJA para aplicar: ').strip() != 'FIJA':
            return
        result = api(ip, cred, 'configManager.cgi?action=setConfig&Network.' + interface + '.DhcpEnable=false&Network.' + interface + '.IPAddress=' + ip)
        if result.strip() != 'OK':
            raise RuntimeError('La camara no acepto el cambio')
        verify = api(ip, cred, 'configManager.cgi?action=getConfig&name=Network')
        if 'Network.' + interface + '.DhcpEnable=false' not in verify:
            raise RuntimeError('No se pudo confirmar IP fija')
        print('IP fija confirmada:', ip)
        return
    try:
        storage = api(ip, cred, 'storageDevice.cgi?action=getDeviceAllInfo')
        old_mode = mode(ip, cred)
    except Exception:
        storage, old_mode = 'No se pudo consultar almacenamiento/modo interno.', None
    if args.inspect:
        print(storage)
        print('Modo:', old_mode)
        print(api(ip, cred, 'configManager.cgi?action=getConfig&name=Network'))
        return
    session = ROOT / 'videos' / datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    session.mkdir(parents=True)
    (session / 'storage_before.txt').write_text(storage)
    total = sum(map(int, re.findall(r'TotalBytes=(\d+)', storage)))
    internal = old_mode is not None and total > 0 and 'IsError=true' not in storage and 'Type=ReadWrite' in storage
    changed = False
    proc = None
    try:
        if internal:
            if state.exists():
                print('Hay una restauracion pendiente. Ejecuta Restaurar-Camara.ps1 antes de cambiar el modo interno.')
            else:
                state.write_text(json.dumps({'ip': ip, 'mode': old_mode}))
                changed = True
                try:
                    mode(ip, cred, 1)
                    print('Camara: orden de grabacion manual confirmada; revisa los archivos de su memoria al terminar.')
                except Exception:
                    print('No se confirmo la grabacion interna; se continuara con la laptop.')
        else:
            print('Camara: no se confirmo memoria escribible. Se grabara en la laptop.')
        url = 'rtsp://{}:{}@{}:554/cam/realmonitor?channel=1&subtype=0'.format(
            urllib.parse.quote(cred['user'], safe=''), urllib.parse.quote(cred['password'], safe=''), ip)
        binary = next((ROOT / 'vendor/imageio_ffmpeg/binaries').glob('ffmpeg*.exe'))
        print('Destino:', session)
        print('ENTER para detener. Video original, sin ejecutar el modelo. Bloques de unos 5 minutos.')
        import threading
        stop = threading.Event()
        def keyboard():
            try:
                input()
                stop.set()
            except EOFError:
                pass
        if not args.seconds:
            threading.Thread(target=keyboard, daemon=True).start()
        start, attempt, failures = time.monotonic(), 0, 0
        while not stop.is_set() and (not args.seconds or time.monotonic() - start < args.seconds):
            if shutil.disk_usage(session).free < 1024**3:
                print('Detenido: queda menos de 1 GB libre.')
                break
            attempt += 1
            cmd = [str(binary), '-hide_banner', '-loglevel', 'error', '-rtsp_transport', 'tcp',
                   '-timeout', '10000000', '-i', url, '-map', '0:v:0', '-c:v', 'copy', '-an',
                   '-f', 'segment', '-segment_time', '300', '-reset_timestamps', '1',
                   str(session / f'toma_{attempt:03d}_%04d.mkv')]
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            def errors(stream):
                with (session / 'registro.txt').open('a', encoding='utf-8') as log:
                    for line in iter(stream.readline, b''):
                        msg = re.sub(r'rtsp://\S+', 'RTSP_OCULTO', line.decode('utf-8', 'replace'))
                        log.write(msg)
                        log.flush()
            threading.Thread(target=errors, args=(proc.stderr,), daemon=True).start()
            previous = 0
            while proc.poll() is None and not stop.wait(1):
                if args.seconds and time.monotonic() - start >= args.seconds:
                    stop.set()
                if shutil.disk_usage(session).free < 1024**3:
                    print('Deteniendo: menos de 1 GB libre.')
                    stop.set()
                size = sum(f.stat().st_size for f in session.glob('*.mkv'))
                if size // (1024**2) > previous:
                    previous = size // (1024**2)
                    print(f'Laptop: {size / 1024**2:.1f} MB guardados')
            if proc.poll() is not None and not stop.is_set():
                current_files = list(session.glob(f'toma_{attempt:03d}_*.mkv'))
                failures = failures + 1 if not any(f.stat().st_size > 4096 for f in current_files) else 0
                if failures >= 3:
                    print('No se pudo grabar tras tres intentos. Revisa IP, credenciales y registro.txt.')
                    break
                print('Conexion interrumpida; reintentando en 3 segundos...')
                stop.wait(3)
    except KeyboardInterrupt:
        print('Deteniendo...')
    finally:
        if proc and proc.poll() is None:
            try:
                proc.stdin.write(b'q\n'); proc.stdin.flush()
                proc.wait(timeout=15)
            except (OSError, subprocess.TimeoutExpired):
                proc.kill(); proc.wait()
        if changed:
            try:
                mode(ip, cred, old_mode)
                state.unlink()
                print('Modo anterior de la camara restaurado.')
            except Exception:
                print('No se pudo restaurar la camara. Usa Restaurar-Camara.ps1 cuando se reconecte.')
        files = [f for f in session.glob('*.mkv') if f.stat().st_size > 0]
        print('Archivos locales:', len(files), '|', session)

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('ERROR:', type(exc).__name__, str(exc) if not isinstance(exc, urllib.error.URLError) else 'No se pudo consultar la camara')
        sys.exit(1)
