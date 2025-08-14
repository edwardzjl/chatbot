import ipaddress
from datetime import datetime, timezone

from fastapi import Request


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


def is_valid_positive_int(value: int | None) -> bool:
    """Helper to check if a value is a positive integer."""
    return isinstance(value, int) and value > 0


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request, considering proxy headers."""
    # Check X-Forwarded-For header (common when behind reverse proxy/load balancer)
    if forwarded_for := request.headers.get("x-forwarded-for"):
        # X-Forwarded-For can contain multiple IPs, take the first one (original client)
        return forwarded_for.split(",")[0].strip()

    # Check X-Real-IP header (common with nginx)
    if real_ip := request.headers.get("x-real-ip"):
        return real_ip.strip()

    # Fall back to direct connection IP
    if request.client and request.client.host:
        return request.client.host

    # Final fallback
    return "unknown"
