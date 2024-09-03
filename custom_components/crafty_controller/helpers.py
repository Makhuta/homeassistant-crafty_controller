from homeassistant.core import HomeAssistant
from crafty_controller_api import Crafty
from typing import Any, Dict

import logging
_LOGGER = logging.getLogger(__name__)

def setup_client(
    username: str,
    password: str,
    host: str,
    port: int,
    ssl: bool,
    verify_ssl: bool
) -> Crafty:
    client = Crafty(host, port, ssl, verify_ssl, username, password)
    return client

def find_dict(list, key, value, default = None):
    for item in list:
        if item.get(key) == value:
            return item
    return default