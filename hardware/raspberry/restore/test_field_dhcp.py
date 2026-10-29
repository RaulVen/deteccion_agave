"""Root-only isolated network test; does not touch the physical Ethernet link."""
import subprocess,sys

def run(*args):
    result=subprocess.run(args,capture_output=True,text=True,timeout=35)
    if result.returncode: raise RuntimeError(' '.join(args)+': '+result.stderr)
    return result.stdout

profile='Agave campo prueba'
ns='agave-field-test'
if subprocess.run(['ip','link','show','agv-test0'],capture_output=True).returncode==0:
    raise SystemExit('Test interface already exists; refusing to replace it')
if profile in run('nmcli','-g','NAME','connection','show').splitlines():
    raise SystemExit('Test profile already exists; refusing to replace it')
if ns in [x.split()[0] for x in run('ip','netns','list').splitlines()]:
    raise SystemExit('Test namespace already exists; refusing to replace it')
try:
    run('ip','netns','add',ns)
    run('ip','link','add','agv-test0','type','veth','peer','name','agv-test1')
    run('ip','link','set','agv-test1','netns',ns)
    run('ip','netns','exec',ns,'ip','link','set','agv-test1','name','eth0')
    run('ip','netns','exec',ns,'ip','link','set','eth0','up')
    run('nmcli','connection','clone','Agave campo directo',profile)
    run('nmcli','connection','modify',profile,'connection.interface-name','agv-test0',
        'ipv4.addresses','192.168.77.239/24','ipv4.shared-dhcp-range','192.168.77.100,192.168.77.150')
    print(run('nmcli','--wait','20','connection','up',profile),flush=True)
    client=r'''
import socket,struct,secrets,json
mac=bytes.fromhex(open('/sys/class/net/eth0/address').read().strip().replace(':',''))
xid=secrets.randbits(32)
header=struct.pack('!BBBBIHH4s4s4s4s16s64s128s',1,1,6,0,xid,0,0x8000,b'\0'*4,b'\0'*4,b'\0'*4,b'\0'*4,mac+b'\0'*10,b'\0'*64,b'\0'*128)+b'\x63\x82\x53\x63'
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
s.setsockopt(socket.SOL_SOCKET,socket.SO_BINDTODEVICE,b'eth0\0')
s.bind(('',68));s.settimeout(8)
raw=socket.socket(socket.AF_PACKET,socket.SOCK_RAW,socket.htons(0x0800))
raw.bind(('eth0',0));raw.settimeout(8)
def receive(kind):
 while True:
  packet,_=raw.recvfrom(4096)
  if len(packet)<42 or packet[23]!=17:continue
  offset=14+(packet[14]&15)*4
  if struct.unpack('!H',packet[offset+2:offset+4])[0]!=68:continue
  data=packet[offset+8:]
  if len(data)<240:continue
  if struct.unpack('!I',data[4:8])[0]!=xid:continue
  opts={};i=240
  while i<len(data) and data[i]!=255:
   k=data[i];i+=1
   if k==0:continue
   n=data[i];i+=1;opts[k]=data[i:i+n];i+=n
  if opts.get(53)==bytes([kind]):return data,opts
s.sendto(header+b'\x35\x01\x01\xff',('255.255.255.255',67))
offer,options=receive(2)
address=offer[16:20];server=options[54]
s.sendto(header+b'\x35\x01\x03\x32\x04'+address+b'\x36\x04'+server+b'\xff',('255.255.255.255',67))
ack,_=receive(5)
print(json.dumps({'dhcp_ack':True,'assigned_ip':socket.inet_ntoa(ack[16:20]),'server':socket.inet_ntoa(server)}))
'''
    print(run('ip','netns','exec',ns,'python3','-c',client),flush=True)
finally:
    subprocess.run(['nmcli','connection','delete',profile],capture_output=True)
    subprocess.run(['ip','link','delete','agv-test0'],capture_output=True)
    subprocess.run(['ip','netns','delete',ns],capture_output=True)
