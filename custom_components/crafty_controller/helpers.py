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

def parse_size(input:str) -> tuple[float, str]:
    import re
    try:
        input_match = re.search(r"([\d.]+)([a-zA-Z]+)", input)
        input_value = float(input_match.group(1))
        input_unit = str(input_match.group(2))
        return (input_value, input_unit)
    except:
        return (0.0, "B")
        