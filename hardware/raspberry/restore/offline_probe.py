import socket,json
for host,port in [('192.168.1.107',554),('1.1.1.1',443)]:
    try:
        with socket.create_connection((host,port),timeout=2):
            print(json.dumps({'host':host,'connected':True}),flush=True)
    except OSError as e:
        print(json.dumps({'host':host,'connected':False,'errno':e.errno,'error':str(e)}),flush=True)
