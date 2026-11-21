"""Addresses and timeouts of the services core talks to."""

from server.settings.components import config

IMAGES_GRPC_ADDR = config('IMAGES_GRPC_ADDR', default='localhost:50051')
IMAGES_GRPC_TIMEOUT = config('IMAGES_GRPC_TIMEOUT', cast=float, default=10.0)
