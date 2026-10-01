from core.constants import COMMANDS


def validate_command(command):
    parts = command.strip().split()

    if not parts:
        return False

    command_type = parts[0].upper()

    if command_type not in COMMANDS:
        return False

    if command_type in ["PING", "TRACERT", "NSLOOKUP"]:
        return len(parts) == 2

    if command_type == "IPCONFIG":
        return len(parts) == 1

    if command_type == "ROUTE":
        return (
            len(parts) == 2
            and parts[1].upper() == "PRINT"
        )

    if command_type == "ARP":
        return (
            len(parts) == 2
            and parts[1].upper() == "-A"
        )

    if command_type == "NETSTAT":
        return len(parts) == 1

    return False