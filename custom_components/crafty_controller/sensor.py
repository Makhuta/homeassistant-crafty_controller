from typing import Any, Dict, Optional
from collections.abc import Callable
from datetime import datetime

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.const import (
    CONF_NAME, 
    CONF_HOST,
    CONF_PORT,
    EntityCategory,
    )

from .const import DOMAIN
from .coordinator import CraftyDataCoordinator
from .entity import (
    CraftySensorEntity,
    CraftyServiceEntity,
    )
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

import logging
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: Callable,
) -> None:
    coordinator: CraftyDataCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    servers = []
    servers.append(CraftyStateNumbersServersSensor(coordinator, config_entry, True))
    servers.append(CraftyStateNumbersServersSensor(coordinator, config_entry))
    for server in coordinator.data.get("servers"):
        if server.get("server_id"):
            servers.append(CraftyServerStateSensor(coordinator, config_entry, server["server_id"]))
            servers.append(CraftyServerCPUSensor(coordinator, config_entry, server["server_id"]))
            servers.append(CraftyServerMemSensor(coordinator, config_entry, server["server_id"]))
            servers.append(CraftyServerMemPercentSensor(coordinator, config_entry, server["server_id"]))
            servers.append(CraftyServerWorldSizeSensor(coordinator, config_entry, server["server_id"]))
            servers.append(CraftyServerPlayersOnlineSensor(coordinator, config_entry, server["server_id"]))
            servers.append(CraftyServerPlayersMaxSensor(coordinator, config_entry, server["server_id"]))
            servers.append(CraftyServerPlayersUsageSensor(coordinator, config_entry, server["server_id"]))
            servers.append(CraftyServerVersionSensor(coordinator, config_entry, server["server_id"]))

    roles = []
    servers.append(CraftyNumbersRolesSensor(coordinator, config_entry))
    for role in coordinator.data.get("roles"):
        if role.get("role_id"):
            roles.append(CraftyRoleSensor(coordinator, config_entry, role["role_id"]))
            roles.append(CraftyRoleManagerSensor(coordinator, config_entry, role["role_id"]))
            roles.append(CraftyRoleServerStatsSensor(coordinator, config_entry, role["role_id"]))

    users = []
    users.append(CraftyNumbersUsersSensor(coordinator, config_entry))
    for user in coordinator.data.get("users"):
        if user.get("user_id"):
            users.append(CraftyUserCreatedSensor(coordinator, config_entry, user["user_id"]))
            users.append(CraftyUserLoginSensor(coordinator, config_entry, user["user_id"]))
            users.append(CraftyUserUpdateSensor(coordinator, config_entry, user["user_id"]))
            users.append(CraftyUserIPSensor(coordinator, config_entry, user["user_id"]))
            users.append(CraftyUserEmailSensor(coordinator, config_entry, user["user_id"]))
            users.append(CraftyUserEnabledSensor(coordinator, config_entry, user["user_id"]))
            users.append(CraftyUserSuperSensor(coordinator, config_entry, user["user_id"]))
            users.append(CraftyUserRolesSensor(coordinator, config_entry, user["user_id"]))
            users.append(CraftyUserPictureSensor(coordinator, config_entry, user["user_id"]))

    async_add_entities(servers + roles + users, update_before_add=True)

class CraftyStateNumbersServersSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, type: bool = False):
        super().__init__(coordinator, config_entry)
        
        self._name = f'Servers {"Online" if type else "Offline"}'
        self._device_name = "All Servers"
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Servers'
        self._state = lambda x: len([server for server in x.get("servers") if server.get("running") == type])
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_servers_{"online" if type else "offline"}'
        self._icon = "mdi:cloud-outline" if type else "mdi:cloud-off-outline"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self.state_class = SensorStateClass.MEASUREMENT
        
        self._entry_type = DeviceEntryType.SERVICE

class CraftyServerStateSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, server_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'{find_dict(x.get("servers"), "server_id", server_id).get("server_name", server_id) if find_dict(x.get("servers"), "server_id", server_id) else server_id} state'
        self._device_name = find_dict(self._coordinator.data.get("servers"), "server_id", server_id).get("server_name", server_id) if find_dict(self._coordinator.data.get("servers"), "server_id", server_id) else server_id
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Server'
        self._state = lambda x: ("Online" if find_dict(x.get("servers"), "server_id", server_id).get("running") else "Offline") if find_dict(x.get("servers"), "server_id", server_id) else None
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_server_state_{server_id}'
        self._icon = lambda x: "mdi:server" if self._state(x) == "Online" else "mdi:server-off"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller Server State {server_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")

        via_device_name = "All Servers"
        via_device_model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Servers'

        self._via_device = f'{self._host}_{self._port}_Crafty_Controller_{via_device_name}_{via_device_model}'

class CraftyServerCPUSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, server_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'{find_dict(x.get("servers"), "server_id", server_id).get("server_name", server_id) if find_dict(x.get("servers"), "server_id", server_id) else server_id} CPU'
        self._device_name = find_dict(self._coordinator.data.get("servers"), "server_id", server_id).get("server_name", server_id) if find_dict(self._coordinator.data.get("servers"), "server_id", server_id) else server_id
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Server'
        self._state = lambda x: (find_dict(x.get("servers"), "server_id", server_id).get("cpu", 0)) if find_dict(x.get("servers"), "server_id", server_id) else 0
        self._unit = "%"
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_server_cpu_{server_id}'
        self._icon = "mdi:cpu-64-bit"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller Server CPU {server_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")

        via_device_name = "All Servers"
        via_device_model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Servers'

        self._via_device = f'{self._host}_{self._port}_Crafty_Controller_{via_device_name}_{via_device_model}'

class CraftyServerMemSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, server_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'{find_dict(x.get("servers"), "server_id", server_id).get("server_name", server_id) if find_dict(x.get("servers"), "server_id", server_id) else server_id} Memory'
        self._device_name = find_dict(self._coordinator.data.get("servers"), "server_id", server_id).get("server_name", server_id) if find_dict(self._coordinator.data.get("servers"), "server_id", server_id) else server_id
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Server'
        self._state = lambda x: (find_dict(x.get("servers"), "server_id", server_id).get("mem", 0)) if find_dict(x.get("servers"), "server_id", server_id) else 0
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_server_mem_{server_id}'
        self._icon = "mdi:memory"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller Server Memory {server_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")

        via_device_name = "All Servers"
        via_device_model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Servers'

        self._via_device = f'{self._host}_{self._port}_Crafty_Controller_{via_device_name}_{via_device_model}'

class CraftyServerMemPercentSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, server_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'{find_dict(x.get("servers"), "server_id", server_id).get("server_name", server_id) if find_dict(x.get("servers"), "server_id", server_id) else server_id} Memory usage'
        self._device_name = find_dict(self._coordinator.data.get("servers"), "server_id", server_id).get("server_name", server_id) if find_dict(self._coordinator.data.get("servers"), "server_id", server_id) else server_id
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Server'
        self._state = lambda x: (find_dict(x.get("servers"), "server_id", server_id).get("mem_percent", 0)) if find_dict(x.get("servers"), "server_id", server_id) else 0
        self._unit = "%"
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_server_mem_usage_{server_id}'
        self._icon = "mdi:memory"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller Server Memory usage {server_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")

        via_device_name = "All Servers"
        via_device_model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Servers'

        self._via_device = f'{self._host}_{self._port}_Crafty_Controller_{via_device_name}_{via_device_model}'

class CraftyServerWorldSizeSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, server_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'{find_dict(x.get("servers"), "server_id", server_id).get("server_name", server_id) if find_dict(x.get("servers"), "server_id", server_id) else server_id} World size'
        self._device_name = find_dict(self._coordinator.data.get("servers"), "server_id", server_id).get("server_name", server_id) if find_dict(self._coordinator.data.get("servers"), "server_id", server_id) else server_id
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Server'
        self._state = lambda x: (find_dict(x.get("servers"), "server_id", server_id).get("world_size", 0)) if find_dict(x.get("servers"), "server_id", server_id) else 0
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_server_world_size_{server_id}'
        self._icon = "mdi:earth"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller Server World size {server_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")

        via_device_name = "All Servers"
        via_device_model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Servers'

        self._via_device = f'{self._host}_{self._port}_Crafty_Controller_{via_device_name}_{via_device_model}'

class CraftyServerPlayersOnlineSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, server_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'{find_dict(x.get("servers"), "server_id", server_id).get("server_name", server_id) if find_dict(x.get("servers"), "server_id", server_id) else server_id} Number of players'
        self._device_name = find_dict(self._coordinator.data.get("servers"), "server_id", server_id).get("server_name", server_id) if find_dict(self._coordinator.data.get("servers"), "server_id", server_id) else server_id
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Server'
        self._state = lambda x: int((find_dict(x.get("servers"), "server_id", server_id).get("online", 0)) if find_dict(x.get("servers"), "server_id", server_id) else 0)
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_server_number_of_players_{server_id}'
        self._icon = "mdi:account"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller Server Number of players {server_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")
        self.state_class = SensorStateClass.MEASUREMENT

        via_device_name = "All Servers"
        via_device_model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Servers'

        self._via_device = f'{self._host}_{self._port}_Crafty_Controller_{via_device_name}_{via_device_model}'

class CraftyServerPlayersMaxSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, server_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'{find_dict(x.get("servers"), "server_id", server_id).get("server_name", server_id) if find_dict(x.get("servers"), "server_id", server_id) else server_id} Max players'
        self._device_name = find_dict(self._coordinator.data.get("servers"), "server_id", server_id).get("server_name", server_id) if find_dict(self._coordinator.data.get("servers"), "server_id", server_id) else server_id
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Server'
        self._state = lambda x: int((find_dict(x.get("servers"), "server_id", server_id).get("max", 0)) if find_dict(x.get("servers"), "server_id", server_id) else 0)
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_server_max_players_{server_id}'
        self._icon = "mdi:account-group"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller Server Max players {server_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")
        self.state_class = SensorStateClass.MEASUREMENT

        via_device_name = "All Servers"
        via_device_model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Servers'

        self._via_device = f'{self._host}_{self._port}_Crafty_Controller_{via_device_name}_{via_device_model}'

class CraftyServerPlayersUsageSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, server_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'{find_dict(x.get("servers"), "server_id", server_id).get("server_name", server_id) if find_dict(x.get("servers"), "server_id", server_id) else server_id} Player usage'
        self._device_name = find_dict(self._coordinator.data.get("servers"), "server_id", server_id).get("server_name", server_id) if find_dict(self._coordinator.data.get("servers"), "server_id", server_id) else server_id
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Server'
        self._state = lambda x: ((find_dict(x.get("servers"), "server_id", server_id).get("online", 0)) / find_dict(x.get("servers"), "server_id", server_id).get("max", 0)) if find_dict(x.get("servers"), "server_id", server_id) and find_dict(x.get("servers"), "server_id", server_id).get("max", 0) != 0 else 0
        self._unit = "%"
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_server_player_usage_{server_id}'
        self._icon = "mdi:account-question"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller Server Player usage {server_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")

        via_device_name = "All Servers"
        via_device_model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Servers'

        self._via_device = f'{self._host}_{self._port}_Crafty_Controller_{via_device_name}_{via_device_model}'

class CraftyServerVersionSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, server_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'{find_dict(x.get("servers"), "server_id", server_id).get("server_name", server_id) if find_dict(x.get("servers"), "server_id", server_id) else server_id} Version'
        self._device_name = find_dict(self._coordinator.data.get("servers"), "server_id", server_id).get("server_name", server_id) if find_dict(self._coordinator.data.get("servers"), "server_id", server_id) else server_id
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Server'
        self._state = lambda x: (find_dict(x.get("servers"), "server_id", server_id).get("version", 0)) if find_dict(x.get("servers"), "server_id", server_id) else 0
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_server_version_{server_id}'
        self._icon = "mdi:information"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller Server Version {server_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")

        via_device_name = "All Servers"
        via_device_model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Servers'

        self._via_device = f'{self._host}_{self._port}_Crafty_Controller_{via_device_name}_{via_device_model}'


class CraftyNumbersRolesSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, type: bool = False):
        super().__init__(coordinator, config_entry)
        
        self._name = "Roles"
        self._device_name = "All Roles"
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Roles'
        self._state = lambda x: len(x.get("roles", []))
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_roles'
        self._icon = "mdi:account-circle"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self.state_class = SensorStateClass.MEASUREMENT
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller Roles'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")

        self._entry_type = DeviceEntryType.SERVICE

def find_user(users: list, id: int) -> str:
    for user in users:
        if user.get("user_id") == id:
            return user.get("username")
    return id

def find_role(roles: list, id: int) -> str:
    for role in roles:
        if role.get("role_id") == id:
            return role.get("role_name")
    return id

def find_server(servers: list, id: int) -> str:
    return find_dict(servers, "server_id", id).get("server_name", id) if find_dict(servers, "server_id", id) else id

class CraftyRoleSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, role_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'{find_dict(x.get("roles"), "role_id", role_id).get("role_name", role_id) if find_dict(x.get("roles"), "role_id", role_id) else role_id} Users'
        self._device_name = find_dict(self._coordinator.data.get("roles"), "role_id", role_id).get("role_name", role_id) if find_dict(self._coordinator.data.get("roles"), "role_id", role_id) else role_id
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Role'
        self._state = lambda x: len(find_dict(x.get("roles"), "role_id", role_id).get("users", [])) if find_dict(x.get("roles"), "role_id", role_id) else None
        self._attrs = lambda x: {"Users": [find_user(x.get("users"), user_id) for user_id in find_dict(x.get("roles"), "role_id", role_id).get("users", [])]}
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_role_users_{role_id}'
        self._icon = "mdi:account-group"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller Role Users {role_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")

        via_device_name = "All Roles"
        via_device_model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Roles'

        self._via_device = f'{self._host}_{self._port}_Crafty_Controller_{via_device_name}_{via_device_model}'

class CraftyRoleManagerSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, role_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'{find_dict(x.get("roles"), "role_id", role_id).get("role_name", role_id) if find_dict(x.get("roles"), "role_id", role_id) else role_id} Manager'
        self._device_name = find_dict(self._coordinator.data.get("roles"), "role_id", role_id).get("role_name", role_id) if find_dict(self._coordinator.data.get("roles"), "role_id", role_id) else role_id
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Role'
        self._state = lambda x: find_user(x.get("users"), find_dict(x.get("roles"), "role_id", role_id).get("manager", None)) if find_dict(x.get("roles"), "role_id", role_id) else None
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_role_manager_{role_id}'
        self._icon = "mdi:shield-account"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller Role manager {role_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")

        via_device_name = "All Roles"
        via_device_model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Roles'

        self._via_device = f'{self._host}_{self._port}_Crafty_Controller_{via_device_name}_{via_device_model}'

permission_list = [
    "Commands",
    "Terminal",
    "Logs",
    "Schedule",
    "Backup",
    "Files",
    "Config",
    "Players"
]

class CraftyRoleServerStatsSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, role_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'{find_dict(x.get("roles"), "role_id", role_id).get("role_name", role_id) if find_dict(x.get("roles"), "role_id", role_id) else role_id} Server access'
        self._device_name = find_dict(self._coordinator.data.get("roles"), "role_id", role_id).get("role_name", role_id) if find_dict(self._coordinator.data.get("roles"), "role_id", role_id) else role_id
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Role'
        self._state = lambda x: len(find_dict(x.get("roles"), "role_id", role_id).get("servers", [])) if find_dict(x.get("roles"), "role_id", role_id) else None
        self._attrs = lambda x: {find_server(self._coordinator.data.get("servers"), server.get("server_id")): {permission_list[idx]: int(permission) == 1 for idx, permission in enumerate([*server.get("permissions", "")])} for server in find_dict(x.get("roles"), "role_id", role_id).get("servers", [])}
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_role_server_access_{role_id}'
        self._icon = "mdi:server-security"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller Role Server access {role_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")

        via_device_name = "All Roles"
        via_device_model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Roles'

        self._via_device = f'{self._host}_{self._port}_Crafty_Controller_{via_device_name}_{via_device_model}'



class CraftyNumbersUsersSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, type: bool = False):
        super().__init__(coordinator, config_entry)
        
        self._name = "Users"
        self._device_name = "All Users"
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Users'
        self._state = lambda x: len(x.get("users", []))
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_users'
        self._icon = "mdi:account-group"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self.state_class = SensorStateClass.MEASUREMENT
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller Roles'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")

        self._entry_type = DeviceEntryType.SERVICE

class CraftyUserCreatedSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, user_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'{find_dict(x.get("users"), "user_id", user_id).get("username", user_id) if find_dict(x.get("users"), "user_id", user_id) else user_id} Created'
        self._device_name = find_dict(self._coordinator.data.get("users"), "user_id", user_id).get("username", user_id) if find_dict(self._coordinator.data.get("users"), "user_id", user_id) else user_id
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}User'
        self._state = lambda x: find_dict(x.get("users"), "user_id", user_id).get("created") if find_dict(x.get("users"), "user_id", user_id) else None
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_user_{user_id}'
        self._unit = None
        self._icon = "mdi:account"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller User {user_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")

        via_device_name = "All Users"
        via_device_model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Users'

        self._via_device = f'{self._host}_{self._port}_Crafty_Controller_{via_device_name}_{via_device_model}'

class CraftyUserLoginSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, user_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'{find_dict(x.get("users"), "user_id", user_id).get("username", user_id) if find_dict(x.get("users"), "user_id", user_id) else user_id} Last login'
        self._device_name = find_dict(self._coordinator.data.get("users"), "user_id", user_id).get("username", user_id) if find_dict(self._coordinator.data.get("users"), "user_id", user_id) else user_id
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}User'
        self._state: datetime = lambda x: find_dict(x.get("users"), "user_id", user_id).get("last_login") if find_dict(x.get("users"), "user_id", user_id) else None
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_user_last_login_{user_id}'
        self._icon = "mdi:login"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller User Last login {user_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")

        via_device_name = "All Users"
        via_device_model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Users'

        self._via_device = f'{self._host}_{self._port}_Crafty_Controller_{via_device_name}_{via_device_model}'

class CraftyUserUpdateSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, user_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'{find_dict(x.get("users"), "user_id", user_id).get("username", user_id) if find_dict(x.get("users"), "user_id", user_id) else user_id} Last update'
        self._device_name = find_dict(self._coordinator.data.get("users"), "user_id", user_id).get("username", user_id) if find_dict(self._coordinator.data.get("users"), "user_id", user_id) else user_id
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}User'
        self._state: datetime = lambda x: find_dict(x.get("users"), "user_id", user_id).get("last_update") if find_dict(x.get("users"), "user_id", user_id) else None
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_user_last_update_{user_id}'
        self._icon = "mdi:update"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller User Last update {user_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")

        via_device_name = "All Users"
        via_device_model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Users'

        self._via_device = f'{self._host}_{self._port}_Crafty_Controller_{via_device_name}_{via_device_model}'
        
class CraftyUserIPSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, user_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'{find_dict(x.get("users"), "user_id", user_id).get("username", user_id) if find_dict(x.get("users"), "user_id", user_id) else user_id} Last IP'
        self._device_name = find_dict(self._coordinator.data.get("users"), "user_id", user_id).get("username", user_id) if find_dict(self._coordinator.data.get("users"), "user_id", user_id) else user_id
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}User'
        self._state = lambda x: find_dict(x.get("users"), "user_id", user_id).get("last_ip") if find_dict(x.get("users"), "user_id", user_id) else None
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_user_last_ip_{user_id}'
        self._icon = "mdi:ip"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller User Last IP {user_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")

        via_device_name = "All Users"
        via_device_model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Users'

        self._via_device = f'{self._host}_{self._port}_Crafty_Controller_{via_device_name}_{via_device_model}'
                
class CraftyUserEmailSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, user_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'{find_dict(x.get("users"), "user_id", user_id).get("username", user_id) if find_dict(x.get("users"), "user_id", user_id) else user_id} Email'
        self._device_name = find_dict(self._coordinator.data.get("users"), "user_id", user_id).get("username", user_id) if find_dict(self._coordinator.data.get("users"), "user_id", user_id) else user_id
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}User'
        self._state = lambda x: find_dict(x.get("users"), "user_id", user_id).get("email") if find_dict(x.get("users"), "user_id", user_id) else None
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_user_email_{user_id}'
        self._icon = "mdi:email"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller User Email {user_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")

        via_device_name = "All Users"
        via_device_model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Users'

        self._via_device = f'{self._host}_{self._port}_Crafty_Controller_{via_device_name}_{via_device_model}'
                
class CraftyUserEnabledSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, user_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'{find_dict(x.get("users"), "user_id", user_id).get("username", user_id) if find_dict(x.get("users"), "user_id", user_id) else user_id} Enabled'
        self._device_name = find_dict(self._coordinator.data.get("users"), "user_id", user_id).get("username", user_id) if find_dict(self._coordinator.data.get("users"), "user_id", user_id) else user_id
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}User'
        self._state: bool = lambda x: find_dict(x.get("users"), "user_id", user_id).get("enabled") if find_dict(x.get("users"), "user_id", user_id) else False
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_user_enabled_{user_id}'
        self._icon = lambda x: "mdi:account-check" if (find_dict(x.get("users"), "user_id", user_id).get("enabled") if find_dict(x.get("users"), "user_id", user_id) else False) else "mdi:account-cancel"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller User Enabled {user_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")

        via_device_name = "All Users"
        via_device_model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Users'

        self._via_device = f'{self._host}_{self._port}_Crafty_Controller_{via_device_name}_{via_device_model}'
                        
class CraftyUserSuperSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, user_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'{find_dict(x.get("users"), "user_id", user_id).get("username", user_id) if find_dict(x.get("users"), "user_id", user_id) else user_id} Superuser'
        self._device_name = find_dict(self._coordinator.data.get("users"), "user_id", user_id).get("username", user_id) if find_dict(self._coordinator.data.get("users"), "user_id", user_id) else user_id
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}User'
        self._state: bool = lambda x: find_dict(x.get("users"), "user_id", user_id).get("superuser") if find_dict(x.get("users"), "user_id", user_id) else False
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_user_superuser_{user_id}'
        self._icon = "mdi:account-supervisor"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller User Superuser {user_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")

        via_device_name = "All Users"
        via_device_model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Users'

        self._via_device = f'{self._host}_{self._port}_Crafty_Controller_{via_device_name}_{via_device_model}'

class CraftyUserRolesSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, user_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'{find_dict(x.get("users"), "user_id", user_id).get("username", user_id) if find_dict(x.get("users"), "user_id", user_id) else user_id} Roles'
        self._device_name = find_dict(self._coordinator.data.get("users"), "user_id", user_id).get("username", user_id) if find_dict(self._coordinator.data.get("users"), "user_id", user_id) else user_id
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}User'
        self._state = lambda x: len(find_dict(x.get("users"), "user_id", user_id).get("roles") if find_dict(x.get("users"), "user_id", user_id) else [])
        self._attrs = lambda x: {"Roles": [find_role(x.get("roles"), role.get("role_id")) for role in (find_dict(x.get("users"), "user_id", user_id).get("roles") if find_dict(x.get("users"), "user_id", user_id) else [])]}
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_user_roles_{user_id}'
        self._icon = "mdi:account-supervisor"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller User Roles {user_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")

        via_device_name = "All Users"
        via_device_model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Users'

        self._via_device = f'{self._host}_{self._port}_Crafty_Controller_{via_device_name}_{via_device_model}'

class CraftyUserPictureSensor(CraftySensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, user_id: int):
        super().__init__(coordinator, config_entry)
        
        self._name = lambda x: f'{find_dict(x.get("users"), "user_id", user_id).get("username", user_id) if find_dict(x.get("users"), "user_id", user_id) else user_id} Picture'
        self._device_name = find_dict(self._coordinator.data.get("users"), "user_id", user_id).get("username", user_id) if find_dict(self._coordinator.data.get("users"), "user_id", user_id) else user_id
        self._model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}User'
        self._state = lambda x: find_dict(x.get("users"), "user_id", user_id).get("picture") if find_dict(x.get("users"), "user_id", user_id) else None
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller_user_picture_{user_id}'
        self._icon = "mdi:badge-account-horizontal"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        id = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller User Picture {user_id}'
        self.entity_id = f'sensor.{id}'.lower().replace(" ", "_")

        via_device_name = "All Users"
        via_device_model = f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Users'

        self._via_device = f'{self._host}_{self._port}_Crafty_Controller_{via_device_name}_{via_device_model}'
