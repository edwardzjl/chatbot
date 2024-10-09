from asyncio import sleep

from loguru import logger
from prometheus_client import Gauge
from psycopg_pool.base import BasePool

psycopg_requests_num = Gauge("psycopg_requests_num", "Total number of requests made")
psycopg_requests_queued = Gauge("psycopg_requests_queued", "Number of requests queued")
psycopg_connections_num = Gauge(
    "psycopg_connections_num", "Total number of connections"
)
psycopg_connections_ms = Gauge(
    "psycopg_connections_ms", "Total connection time in milliseconds"
)
psycopg_requests_wait_ms = Gauge(
    "psycopg_requests_wait_ms", "Total wait time for requests in milliseconds"
)
psycopg_usage_ms = Gauge("psycopg_usage_ms", "Total usage time in milliseconds")
psycopg_connections_lost = Gauge(
    "psycopg_connections_lost", "Number of lost connections"
)
psycopg_pool_min = Gauge(
    "psycopg_pool_min", "Minimum number of connections in the pool"
)
psycopg_pool_max = Gauge(
    "psycopg_pool_max", "Maximum number of connections in the pool"
)
psycopg_pool_size = Gauge("psycopg_pool_size", "Current pool size")
psycopg_pool_available = Gauge(
    "psycopg_pool_available", "Number of available connections in the pool"
)
psycopg_requests_waiting = Gauge(
    "psycopg_requests_waiting", "Number of waiting requests"
)


async def update_psycopg_metrics(conn_pool: BasePool, interval: int = 10) -> None:
    while True:
        try:
            stats = conn_pool.get_stats()

            psycopg_requests_num.set(stats["requests_num"])
            psycopg_requests_queued.set(stats["requests_queued"])
            psycopg_connections_num.set(stats["connections_num"])
            psycopg_connections_ms.set(stats["connections_ms"])
            psycopg_requests_wait_ms.set(stats["requests_wait_ms"])
            psycopg_usage_ms.set(stats["usage_ms"])
            if (connections_lost := stats.get("connections_lost")) is not None:
                psycopg_connections_lost.set(connections_lost)
            psycopg_pool_min.set(stats["pool_min"])
            psycopg_pool_max.set(stats["pool_max"])
            psycopg_pool_size.set(stats["pool_size"])
            psycopg_pool_available.set(stats["pool_available"])
            psycopg_requests_waiting.set(stats["requests_waiting"])
        except Exception:
            logger.exception("Unknown error occured")
        finally:
            await sleep(interval)
