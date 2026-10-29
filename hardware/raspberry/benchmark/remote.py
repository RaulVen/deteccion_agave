"""SSH runner; password is supplied via RPI_PASSWORD, never saved here."""
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
import paramiko

client = paramiko.SSHClient()
client.load_system_host_keys()
client.connect("pa-bioiot", username="bioiot", password=os.environ["RPI_PASSWORD"],
               look_for_keys=False, allow_agent=False, timeout=15)
try:
    if sys.argv[1] == "put":
        with client.open_sftp() as sftp:
            sftp.put(sys.argv[2], sys.argv[3])
        print("Uploaded", Path(sys.argv[2]).name)
    elif sys.argv[1] == "get":
        with client.open_sftp() as sftp:
            sftp.get(sys.argv[2], sys.argv[3])
        print("Downloaded", Path(sys.argv[3]).name)
    else:
        command = sys.argv[2]
        if sys.argv[1] == "sudo":
            command = "sudo -S -p '' " + command
        stdin, stdout, stderr = client.exec_command(command, timeout=1800)
        if sys.argv[1] == "sudo":
            stdin.write(os.environ["RPI_PASSWORD"] + "\n")
            stdin.flush()
        for line in stdout:
            print(line, end="", flush=True)
        print(stderr.read().decode("utf-8", "replace"), end="")
        sys.exit(stdout.channel.recv_exit_status())
finally:
    client.close()
