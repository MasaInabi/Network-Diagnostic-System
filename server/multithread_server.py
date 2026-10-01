import socket
import subprocess
import time
import threading
from datetime import datetime
import sys
sys.path.append(".")
from config.config_loader import load_config

config = load_config()

HOST = "127.0.0.1"
PORT = config["tcp_port"]
MAX_CLIENTS = config["max_clients"]
LOG_FILE = config["log_file"]


def handle_client(c, a):
    print("Client connected:", a)

    try:
        d = c.recv(1024)

        if not d:
            return

        cmd = d.decode()

        print("Received from", a, ":", cmd)

        t1 = time.time()

        r = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )

        t2 = time.time()

        et = t2 - t1
        ts = datetime.now()

        if r.returncode == 0:
            st = "Success"
            out = r.stdout
        else:
            st = "Failure"
            out = r.stderr

        ip = a[0]
        port = a[1]

        p = cmd.split()

        if len(p) > 1:
            par = p[1]
        else:
            par = "None"

        f = open(LOG_FILE, "a")

        f.write(
            str(ts) + "," +
            ip + "," +
            str(port) + "," +
            cmd + "," +
            par + "," +
            str(et) + "," +
            st + "\n"
        )

        f.close()

        msg = (
            "Status: " + st +
            "\nExecution Time: " + str(et) +
            "\nTimestamp: " + str(ts) +
            "\nOutput:\n" + out
        )

        c.send(msg.encode())

    except Exception as e:
        print("Error with client", a, ":", e)

    finally:
        c.close()
        print("Client disconnected:", a)


s = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

s.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

s.bind((HOST, PORT))

s.listen(MAX_CLIENTS)

print("Multi-threaded Server is running...")
print("Waiting for clients...")


while True:
    c, a = s.accept()

    t = threading.Thread(
        target=handle_client,
        args=(c, a)
    )

    t.start()

    print(
        "New thread started:",
        t.name
    )