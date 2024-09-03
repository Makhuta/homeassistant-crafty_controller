from typing import Any, Callable, Dict, Optional

from homeassistant.const import CONF_NAME
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from crafty_controller_api import ServerActions

from .const import DOMAIN
from .coordinator import CraftyDataCoordinator
from .entity import CraftyButtonEntity
from .helpers import find_dict

action_types = [
        {
            "action": ServerActions.START_SERVER,
            "name": "Start server",
            "icon": "mdi:play"
        },
        {
            "action": ServerActions.STOP_SERVER,
            "name": "Stop server",
            "icon": "mdi:stop"
        },
        {
            "action": ServerActions.RESTART_SERVER,
            "name": "Restart server",
            "icon": "mdi:restart"
        },
        {
            "action": ServerActions.KILL_SERVER,
            "name": "Kill server",
            "icon": "mdi:power"
        },
        {
            "action": ServerActions.BACKUP_SERVER,
            "name": "Backup server",
            "icon": "mdi:cloud-upload"            
        }
    ]



import logging
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: Callable,
) -> None:
    """Set up Crafty button from config entry."""
    coordinator: CraftyDataCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    servers = [CraftyServerButton(coordinator, config_entry, hass, server["server_id"], type) for type in action_types for server in coordinator.data.get("servers") if server.get("server_id")]

    async_add_entities(servers, update_before_add=True)

def action_decorator(hass, id, action):
    async def func(client):
        await hass.async_add_executor_job(client.server_action, id, action)

    return func


class CraftyServerButton(CraftyButtonEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, hass: HomeAssistant, server_id: int, type: dict[str, Any]):
        super().__init__(coordinator, config_entry, hass)

        self._name = lambda x: f'{type.get("name")}'
        self._device_name = find_dict(self._coordinator.data.get("servers"), "server_id", server_id).get("server_name", server_id) if find_dict(self._coordinator.data.get("servers"), "server_id", server_id) else server_id
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Server'
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_server_{type.get("action")}_{server_id}'
        self._icon = type.get("icon")
        self._attr_entity_category = None
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller Server {type.get("name")} {server_id}'
        self.entity_id = f'button.{id}'.lower().replace(" ", "_")
        self._action = action_decorator(self._hass, server_id, type.get("action"))

        via_device_name = "All Servers"
        via_device_model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Servers'

        self._via_device = f'{self._host}_{self._port}_Crafty_Controller_{via_device_name}_{via_device_model}' #f'{self._host}_{self._port}_Crafty_Controller_server_{server_id}'

