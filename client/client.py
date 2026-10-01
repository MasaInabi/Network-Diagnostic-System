import socket
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.config_loader import load_config
from core.protocol import receive_message


config = load_config()

HOST = config["host"]
PORT = config["tcp_port"]


def show_menu():

    print()
    print("=====================================")
    print("Network Diagnostic System")
    print("=====================================")

    print("1. Ping Host")
    print("2. Trace Route")
    print("3. DNS Lookup")
    print("4. IP Configuration")
    print("5. Routing Table")
    print("6. ARP Table")
    print("7. Active TCP Connections")
    print("8. Exit")


def create_command(choice):

    if choice == "1":

        host = input("Enter host: ").strip()

        if host == "":
            return None

        return "PING " + host

    elif choice == "2":

        host = input("Enter host: ").strip()

        if host == "":
            return None

        return "TRACERT " + host

    elif choice == "3":

        host = input("Enter host: ").strip()

        if host == "":
            return None

        return "NSLOOKUP " + host

    elif choice == "4":

        return "IPCONFIG"

    elif choice == "5":

        return "ROUTE PRINT"

    elif choice == "6":

        return "ARP -A"

    elif choice == "7":

        return "NETSTAT"

    return None


def main():

    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:

        client.connect(
            (HOST, PORT)
        )

        confirmation = receive_message(
            client
        )

        if confirmation:
            print(confirmation)

        while True:

            show_menu()

            choice = input(
                "Select: "
            ).strip()

            if choice == "8":

                client.sendall(
                    b"EXIT\n"
                )

                print(
                    "Disconnected from server."
                )

                break

            command = create_command(
                choice
            )

            if command is None:

                print(
                    "Invalid choice or host."
                )

                continue

            client.sendall(
                (
                    command + "\n"
                ).encode("utf-8")
            )

            result = receive_message(
                client
            )

            if result is None:

                print(
                    "Server disconnected."
                )

                break

            print()
            print(result)

            input(
                "\nPress ENTER to continue..."
            )

    except ConnectionRefusedError:

        print(
            "Could not connect to server."
        )

    except Exception as error:

        print(
            "Client error:",
            error
        )

    finally:

        client.close()


if __name__ == "__main__":
    main()