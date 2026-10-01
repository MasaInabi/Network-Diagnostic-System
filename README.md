# Network Diagnostic System

A Python-based client-server network diagnostic system developed as part of the ENCS3320 Computer Networks course.

## Features

- Client-server communication using TCP sockets
- Supports multiple clients using multithreading
- Executes common network diagnostic commands
- Stores command execution details in log files
- Provides an HTTP web dashboard
- Displays command history and statistics
- Supports searching and downloading logs
- Uses a JSON configuration file for system settings

## Network Diagnostic Commands

The system supports:

- Ping
- Traceroute
- DNS Lookup
- IP Configuration
- Routing Table
- ARP Table
- Active TCP Connections

## Technologies

- Python
- TCP Sockets
- HTTP
- Multithreading
- JSON
- HTML

## Project Structure

- `client/` – Client-side implementation
- `server/` – Server-side implementation
- `core/` – Core functionality
- `web/` – HTTP dashboard
- `config/` – Configuration files
- `screenshots/` – Project screenshots
- `run_client.py` – Starts the client
- `run_server.py` – Starts the server

## How to Run

1. Clone or download the repository.
2. Make sure Python is installed.
3. Start the server:

   `python run_server.py`

4. Start the client:

   `python run_client.py`

5. Select a network diagnostic command from the client menu.

## Course

ENCS3320 – Computer Networks
