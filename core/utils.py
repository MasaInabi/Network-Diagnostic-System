from datetime import datetime


def get_timestamp():
    return datetime.now()


def get_timestamp_string():
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )