import socket
import subprocess
import time
import threading
from datetime import datetime
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from config.config_loader import load_config
from core.protocol import recv_line, send_message
from core.validation import validate_command


config = load_config()

HOST = config["host"]
PORT = config["tcp_port"]
MAX_CLIENTS = config["max_clients"]
LOG_FILE = PROJECT_ROOT / config["log_file"]


log_lock = threading.Lock()


def build_system_command(command):

    parts = command.split()

    if not parts:
        return None, "None"

    command_type = parts[0].upper()

    if command_type == "PING" and len(parts) == 2:
        return ["ping", parts[1]], parts[1]

    if command_type == "TRACERT" and len(parts) == 2:
        return ["tracert", parts[1]], parts[1]

    if command_type == "NSLOOKUP" and len(parts) == 2:
        return ["nslookup", parts[1]], parts[1]

    if command_type == "IPCONFIG" and len(parts) == 1:
        return ["ipconfig"], "None"

    if (
        command_type == "ROUTE"
        and len(parts) == 2
        and parts[1].upper() == "PRINT"
    ):
        return ["route", "print"], "None"

    if (
        command_type == "ARP"
        and len(parts) == 2
        and parts[1].upper() == "-A"
    ):
        return ["arp", "-a"], "None"

    if command_type == "NETSTAT" and len(parts) == 1:
        return ["netstat", "-ano"], "None"

    return None, "None"


def write_log(
    timestamp,
    address,
    command,
    parameter,
    execution_time,
    status
):

    LOG_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    line = (
        str(timestamp) + "," +
        address[0] + "," +
        str(address[1]) + "," +
        command + "," +
        parameter + "," +
        str(execution_time) + "," +
        status + "\n"
    )

    with log_lock:

        with open(
            LOG_FILE,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(line)


def execute_command(command, address):

    timestamp = datetime.now()

    if not validate_command(command):

        status = "Failure"
        execution_time = 0
        output = "Invalid or unsupported command."
        parameter = "None"

    else:

        system_command, parameter = build_system_command(
            command
        )

        start_time = time.time()

        try:

            result = subprocess.run(
                system_command,
                capture_output=True,
                text=True,
                timeout=60,
                shell=False
            )

            execution_time = (
                time.time() - start_time
            )

            if result.returncode == 0:

                status = "Success"
                output = result.stdout

            else:

                status = "Failure"

                output = (
                    result.stderr
                    if result.stderr
                    else result.stdout
                )

        except subprocess.TimeoutExpired:

            execution_time = (
                time.time() - start_time
            )

            status = "Failure"
            output = "Command timed out."

        except Exception as error:

            execution_time = (
                time.time() - start_time
            )

            status = "Failure"
            output = str(error)

    write_log(
        timestamp,
        address,
        command,
        parameter,
        execution_time,
        status
    )

    response = (
        "Status: " + status +
        "\nExecution Time: " +
        str(execution_time) +
        "\nTimestamp: " +
        str(timestamp) +
        "\nOutput:\n" +
        output
    )

    return response


def handle_client(
    client_socket,
    address
):

    print(
        "Client connected:",
        address
    )

    try:

        send_message(
            client_socket,
            "Connected to Network Diagnostic Server."
        )

        while True:

            command = recv_line(
                client_socket
            )

            if command is None:
                break

            command = command.strip()

            if command == "":
                continue

            print(
                "Received from",
                address,
                ":",
                command
            )

            if command.upper() == "EXIT":
                break

            response = execute_command(
                command,
                address
            )

            send_message(
                client_socket,
                response
            )

    except Exception as error:

        print(
            "Error with client",
            address,
            ":",
            error
        )

    finally:

        client_socket.close()

        print(
            "Client disconnected:",
            address
        )


def start_tcp_server():

    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server_socket.bind(
        (HOST, PORT)
    )

    server_socket.listen(
        MAX_CLIENTS
    )

    print(
        "TCP Server started on port",
        PORT
    )

    print(
        "Waiting for client connections..."
    )

    try:

        while True:

            client_socket, address = (
                server_socket.accept()
            )

            thread = threading.Thread(
                target=handle_client,
                args=(
                    client_socket,
                    address
                )
            )

            thread.start()

            print(
                thread.name,
                "created."
            )

    except KeyboardInterrupt:

        print(
            "\nTCP Server stopped."
        )

    finally:

        server_socket.close()


if __name__ == "__main__":
    start_tcp_server()