import threading

from web.http_server import start_http_server
from server.server import start_tcp_server
from config.config_loader import load_config


def main():
    config = load_config()

    print("Loading configuration...")
    print("TCP Port:", config["tcp_port"])
    print("HTTP Port:", config["http_port"])

    http_thread = threading.Thread(
        target=start_http_server
    )

    http_thread.daemon = True
    http_thread.start()

    start_tcp_server()


if __name__ == "__main__":
    main()