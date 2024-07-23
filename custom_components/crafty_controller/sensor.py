from typing import Any, Dict, Optional
from collections.abc import Callable

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    CONF_NAME, 
    CONF_HOST,
    CONF_PORT,
    EntityCategory,
    )

from .const import DOMAIN
from .coordinator import CraftyDataCoordinator
from .entity import CraftySensorEntity
from .helpers import find_dict

def is_online(data: dict[str, Any]) -> bool:
    for key, value in data.items():
        if type(value) == dict and len(value.keys()) > 0:
            return True
        if type(value) == list and len(value) > 0:
            return True

    return False

async def awaiting_coroutine(hass, cor):
    return await hass.async_add_executor_job(cor)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: Callable,
) -> None:
    coordinator: CraftyDataCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    roles = [CraftyRoleSensor(coordinator, config_entry, role["role_id"]) for role in coordinator.data.get("roles") if role.get("role_id")]
    servers = [CraftyServerSensor(coordinator, config_entry, server["server_id"]) for server in coordinator.data.get("servers") if server.get("server_id")]
    users = [CraftyUserSensor(coordinator, config_entry, user["user_id"]) for user in coordinator.data.get("users") if user.get("user_id")]

    async_add_entities(roles + servers + users, update_before_add=True)

class CraftyRoleSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, role_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'Role {find_dict(x.get("roles"), "role_id", role_id).get("role_name", role_id) if find_dict(x.get("roles"), "role_id", role_id) else role_id}'
        self._device_name = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Roles'
        self._model = "Roles"
        self._state = lambda x: len(find_dict(x.get("roles"), "role_id", role_id).get("users", [])) if find_dict(x.get("roles"), "role_id", role_id) else None
        self._attrs = lambda x: find_dict(x.get("roles"), "role_id", role_id)
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_role_{role_id}'
        self._unit = "users"
        self._icon = "mdi:account-group"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller Role {role_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")


class CraftyServerSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, server_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'Server {find_dict(x.get("servers"), "server_id", server_id).get("server_name", server_id) if find_dict(x.get("servers"), "server_id", server_id) else server_id}'
        self._device_name = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Servers'
        self._model = "Servers"
        self._state = lambda x: ("Online" if find_dict(x.get("servers"), "server_id", server_id).get("running") else "Offline") if find_dict(x.get("servers"), "server_id", server_id) else None
        self._attrs = lambda x: find_dict(x.get("servers"), "server_id", server_id)
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_server_{server_id}'
        self._unit = None
        self._icon = "mdi:server"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller Server {server_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")


class CraftyUserSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, user_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'User {find_dict(x.get("users"), "user_id", user_id).get("username", user_id) if find_dict(x.get("users"), "user_id", user_id) else user_id}'
        self._device_name = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Users'
        self._model = "Users"
        self._state = lambda x: find_dict(x.get("users"), "user_id", user_id).get("last_login") if find_dict(x.get("users"), "user_id", user_id) else None
        self._attrs = lambda x: find_dict(x.get("users"), "user_id", user_id)
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_user_{user_id}'
        self._unit = None
        self._icon = "mdi:account"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller User {user_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")
