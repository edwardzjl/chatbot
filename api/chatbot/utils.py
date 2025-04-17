import ipaddress
from datetime import datetime, timezone


def utcnow():
    """
    `datetime.datetime.utcnow()` does not contain timezone information.
    """
    return datetime.now(timezone.utc)


def is_public_ip(ip_str: str):
    """Check if the given IP address is public.
    Args:
        ip_str (str): The IP address to check.
    Returns:
        bool: True if the IP address is public, False otherwise.
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        return ip.is_global
    except ValueError:
        # Invalid IP address
        return False
