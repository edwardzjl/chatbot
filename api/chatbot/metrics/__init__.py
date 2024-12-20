from prometheus_client import Gauge

connected_clients = Gauge("connected_ws_clients", "Total Connected Websocket Clients")
