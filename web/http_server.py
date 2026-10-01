import socket
import subprocess
import time
import os

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.config_loader import load_config

config = load_config()

HOST = config["host"]
TCP_PORT = config["tcp_port"]
HTTP_PORT = config["http_port"]
LOG_FILE = config["log_file"]
DEFAULT_HOMEPAGE = config["default_homepage"]

TEAM_NUMBER = "T026"
STUDENTS = [
    ("Masa", "1231024", "3"),
    ("Nour", "1241254", "3"),
    ("Leqaa", "1230081", "3"),
]

WEB_START_TIME = time.time()


# HTML Helpers
def html_escape(text):
    text = str(text)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def make_page(title, body):
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{}</title>
    <style>
        body {{ font-family: Arial; margin: 40px; }}
        nav a {{ margin-right: 15px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #999; padding: 8px; text-align: left; }}
        th {{ background: #eeeeee; }}
        .box {{ border: 1px solid #aaa; padding: 12px; margin: 8px 0; }}
    </style>
</head>
<body>
    <nav>
        <a href="/">Home</a>
        <a href="/dashboard">Dashboard</a>
        <a href="/history">Command History</a>
        <a href="/statistics">Statistics</a>
        <a href="/search">Search</a>
        <a href="/download">Download</a>
    </nav>
    <hr>
    {}
</body>
</html>""".format(html_escape(title), body)


# ============================================================
# READ PART 2 LOG FILE WITHOUT CHANGING THEIR CODE
# ============================================================
def read_log():
    entries = []

    if not os.path.exists(LOG_FILE):
        return entries

    f = open(LOG_FILE, "r")

    for line in f:
        line = line.strip()

        if line == "":
            continue

        # Their log format has 7 comma-separated fields.
        parts = line.split(",")

        if len(parts) < 7:
            continue

        requested_command = parts[3].strip()
        command_words = requested_command.split()
        command_type = command_words[0].upper() if command_words else ""

        entries.append({
            "timestamp": parts[0].strip(),
            "client_ip": parts[1].strip(),
            "client_port": parts[2].strip(),
            "requested_command": requested_command,
            "command_type": command_type,
            "parameter": parts[4].strip(),
            "execution_time": parts[5].strip(),
            "status": parts[6].strip(),
        })

    f.close()
    return entries


def make_history_table(entries):
    rows = ""

    for entry in entries:
        rows += """
        <tr>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
        </tr>
        """.format(
            html_escape(entry["timestamp"]),
            html_escape(entry["client_ip"]),
            html_escape(entry["requested_command"]),
            html_escape(entry["parameter"]),
            html_escape(entry["execution_time"]),
            html_escape(entry["status"]),
        )

    if rows == "":
        rows = '<tr><td colspan="6">No commands found.</td></tr>'

    return """
    <table>
        <tr>
            <th>Time</th>
            <th>Client IP</th>
            <th>Command</th>
            <th>Parameter</th>
            <th>Execution Time</th>
            <th>Status</th>
        </tr>
        {}
    </table>
    """.format(rows)


# Dashboard Helpers
def get_connected_clients():
    """
    Counts current ESTABLISHED TCP connections whose local port is TCP_PORT.
    This lets Part 3 show connected clients without editing server.py.
    """
    try:
        result = subprocess.run(
            ["netstat", "-an"],
            capture_output=True,
            text=True,
            timeout=3,
        )

        count = 0

        for line in result.stdout.splitlines():
            parts = line.split()

            if os.name == "nt":
                # Windows example:
                # TCP 127.0.0.1:5254 127.0.0.1:50733 ESTABLISHED
                if len(parts) >= 4:
                    protocol = parts[0].upper()
                    local_address = parts[1]
                    state = parts[3].upper()

                    if (
                        protocol == "TCP"
                        and local_address.endswith(":" + str(TCP_PORT))
                        and state == "ESTABLISHED"
                    ):
                        count += 1
            else:
                # Typical Linux netstat format.
                if len(parts) >= 6:
                    protocol = parts[0].upper()
                    local_address = parts[3]
                    state = parts[5].upper()

                    if (
                        protocol.startswith("TCP")
                        and local_address.endswith(":" + str(TCP_PORT))
                        and state == "ESTABLISHED"
                    ):
                        count += 1

        return count

    except Exception:
        return 0


def format_uptime(seconds):
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return "{}h {}m {}s".format(hours, minutes, secs)


# Part 3 Web Pages
def home_page():
    students_html = "<ul>"

    for name, student_id, section in STUDENTS:
        students_html += "<li>{} - ID: {} - Section: {}</li>".format(
            html_escape(name),
            html_escape(student_id),
            html_escape(section),
        )

    students_html += "</ul>"

    body = """
    <h1>Network Diagnostic System</h1>
    <p><b>Team Number:</b> {}</p>

    <h2>Students</h2>
    {}

    <h2>About ENCS3320</h2>
    <p>
        ENCS3320 Computer Networks covers client-server communication,
        TCP socket programming, HTTP, and common network diagnostic operations.
    </p>
    """.format(html_escape(TEAM_NUMBER), students_html)

    return make_page("Home", body)


def dashboard_page():
    entries = read_log()

    total_commands = len(entries)
    connected_clients = get_connected_clients()
    last_execution = "No commands yet"

    if len(entries) > 0:
        last_execution = entries[-1]["timestamp"]

    # Since we are not editing server.py, this is the HTTP server's uptime.
    uptime = format_uptime(time.time() - WEB_START_TIME)

    body = """
    <h1>Dashboard</h1>
    <div class="box"><b>Number of executed commands:</b> {}</div>
    <div class="box"><b>Number of connected clients:</b> {}</div>
    <div class="box"><b>Last execution time:</b> {}</div>
    <div class="box"><b>Server uptime:</b> {}</div>
    """.format(
        total_commands,
        connected_clients,
        html_escape(last_execution),
        uptime,
    )

    return make_page("Dashboard", body)


def history_page():
    entries = read_log()
    body = "<h1>Command History</h1>" + make_history_table(entries)
    return make_page("Command History", body)


def statistics_page():
    entries = read_log()

    command_counts = {}
    total_time = 0.0
    successful = 0
    failed = 0

    for entry in entries:
        command = entry["command_type"]
        command_counts[command] = command_counts.get(command, 0) + 1

        try:
            total_time += float(entry["execution_time"])
        except ValueError:
            pass

        if entry["status"].lower() == "success":
            successful += 1
        else:
            failed += 1

    most_used = "No commands yet"

    for command in command_counts:
        if most_used == "No commands yet":
            most_used = command
        elif command_counts[command] > command_counts[most_used]:
            most_used = command

    average = 0.0
    if len(entries) > 0:
        average = total_time / len(entries)

    body = """
    <h1>Statistics</h1>
    <div class="box"><b>Most frequently used command:</b> {}</div>
    <div class="box"><b>Average execution time:</b> {:.4f} seconds</div>
    <div class="box"><b>Total successful requests:</b> {}</div>
    <div class="box"><b>Total failed requests:</b> {}</div>
    """.format(
        html_escape(most_used),
        average,
        successful,
        failed,
    )

    return make_page("Statistics", body)


def url_decode(text):
    text = text.replace("+", " ")
    result = ""
    i = 0

    while i < len(text):
        if text[i] == "%" and i + 2 < len(text):
            try:
                result += chr(int(text[i + 1:i + 3], 16))
                i += 3
                continue
            except ValueError:
                pass

        result += text[i]
        i += 1

    return result


def parse_query(query_string):
    values = {
        "command": "",
        "hostname": "",
        "client_ip": "",
    }

    if query_string == "":
        return values, None

    for item in query_string.split("&"):
        if "=" in item:
            key, value = item.split("=", 1)
        else:
            key = item
            value = ""

        key = url_decode(key)
        value = url_decode(value)

        if key not in values:
            return None, "Unknown search parameter: " + key

        values[key] = value

    return values, None


def search_page(filters):
    entries = read_log()
    results = []

    command = filters["command"].strip().upper()
    hostname = filters["hostname"].strip().lower()
    client_ip = filters["client_ip"].strip().lower()

    for entry in entries:
        if command != "" and entry["command_type"] != command:
            continue

        if hostname != "":
            searchable = (
                entry["parameter"] + " " + entry["requested_command"]
            ).lower()

            if hostname not in searchable:
                continue

        if client_ip != "" and client_ip not in entry["client_ip"].lower():
            continue

        results.append(entry)

    body = """
    <h1>Search Previous Commands</h1>

    <form method="GET" action="/search">
        Command type:
        <select name="command">
            <option value="">Any</option>
            <option value="PING">PING</option>
            <option value="TRACERT">TRACERT</option>
            <option value="NSLOOKUP">NSLOOKUP</option>
            <option value="IPCONFIG">IPCONFIG</option>
            <option value="ROUTE">ROUTE</option>
            <option value="ARP">ARP</option>
            <option value="NETSTAT">NETSTAT</option>
        </select>

        Hostname:
        <input type="text" name="hostname">

        Client IP:
        <input type="text" name="client_ip">

        <button type="submit">Search</button>
    </form>

    <p>Results: {}</p>
    {}
    """.format(len(results), make_history_table(results))

    return make_page("Search", body)


def download_page():
    body = """
    <h1>Download Log</h1>
    <p>Click below to download the complete log file.</p>
    <p><a href="/download-log">Download log.txt</a></p>
    """
    return make_page("Download", body)


# Part 4: HTTP Responses
def error_page(code, title, message):
    body = """
    <h1>{} {}</h1>
    <p>{}</p>
    <p><a href="/">Return Home</a></p>
    """.format(code, html_escape(title), html_escape(message))

    return make_page("{} {}".format(code, title), body)


def send_html(connection, status_code, status_text, html):
    body = html.encode()

    header = (
        "HTTP/1.1 {} {}\r\n"
        "Content-Type: text/html; charset=UTF-8\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).format(status_code, status_text, len(body))

    connection.sendall(header.encode() + body)


def send_log_file(connection):
    if os.path.exists(LOG_FILE):
        f = open(LOG_FILE, "rb")
        body = f.read()
        f.close()
    else:
        body = b""

    header = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/plain\r\n"
        "Content-Disposition: attachment; filename=\"log.txt\"\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).format(len(body))

    connection.sendall(header.encode() + body)


def handle_request(connection):
    request = connection.recv(4096).decode(errors="ignore")

    if request == "":
        return

    first_line = request.split("\r\n")[0]
    parts = first_line.split()

    # 400 Bad Request: malformed request line.
    if len(parts) != 3:
        send_html(
            connection,
            400,
            "Bad Request",
            error_page(400, "Bad Request", "Malformed HTTP request."),
        )
        return

    method = parts[0]
    target = parts[1]
    version = parts[2]

    # Keep the server intentionally simple: only GET is supported.
    if method != "GET" or not version.startswith("HTTP/"):
        send_html(
            connection,
            400,
            "Bad Request",
            error_page(
                400,
                "Bad Request",
                "Only valid HTTP GET requests are supported.",
            ),
        )
        return

    if "?" in target:
        path, query_string = target.split("?", 1)
    else:
        path = target
        query_string = ""

    # 403 Forbidden: block direct access to project/source files.
    protected_paths = [
        "/server.py",
        "/client.py",
        "/web_server.py",
        "/log.txt",
        "/logs/log.txt",
    ]

    if ".." in path or path in protected_paths:
        send_html(
            connection,
            403,
            "Forbidden",
            error_page(
                403,
                "Forbidden",
                "You are not allowed to access this file directly.",
            ),
        )
        return

    # Known pages: 200 OK.
    if path == DEFAULT_HOMEPAGE:
        send_html(connection, 200, "OK", home_page())

    elif path == "/dashboard":
        send_html(connection, 200, "OK", dashboard_page())

    elif path == "/history":
        send_html(connection, 200, "OK", history_page())

    elif path == "/statistics":
        send_html(connection, 200, "OK", statistics_page())

    elif path == "/search":
        filters, error = parse_query(query_string)

        if error is not None:
            send_html(
                connection,
                400,
                "Bad Request",
                error_page(400, "Bad Request", error),
            )
        else:
            send_html(connection, 200, "OK", search_page(filters))

    elif path == "/download":
        send_html(connection, 200, "OK", download_page())

    elif path == "/download-log":
        send_log_file(connection)

    else:
        # 404 Not Found: custom page for undefined URLs.
        send_html(
            connection,
            404,
            "Not Found",
            error_page(
                404,
                "Not Found",
                "The requested page does not exist.",
            ),
        )


# Raw Socket HTTP Server
def start_http_server():
    web_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    web_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    web_socket.bind((HOST, HTTP_PORT))
    web_socket.listen(5)

    print("HTTP Web Server is running")
    print("Open: http://127.0.0.1:{}".format(HTTP_PORT))
    print("Press Ctrl+C to stop")

    try:
        while True:
            connection, address = web_socket.accept()

            try:
                handle_request(connection)
            finally:
                connection.close()

    except KeyboardInterrupt:
        print("\nHTTP Web Server stopped")

    finally:
        web_socket.close()


if __name__ == "__main__":
    start_http_server()
