def recv_line(client_socket):
    data = b""

    while True:
        char = client_socket.recv(1)

        if not char:
            return None

        if char == b"\n":
            break

        data += char

    return data.decode("utf-8").strip()


def send_message(client_socket, message):
    data = message.encode("utf-8")

    header = str(len(data)).zfill(10).encode("utf-8")

    client_socket.sendall(header + data)


def receive_message(client_socket):
    header = b""

    while len(header) < 10:
        chunk = client_socket.recv(
            10 - len(header)
        )

        if not chunk:
            return None

        header += chunk

    size = int(header.decode("utf-8"))

    data = b""

    while len(data) < size:
        chunk = client_socket.recv(
            min(4096, size - len(data))
        )

        if not chunk:
            return None

        data += chunk

    return data.decode("utf-8")