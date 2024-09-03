from typing import Any, Dict, Optional


from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.const import (
    CONF_NAME, 
    CONF_HOST,
    CONF_PORT,
    )

from .const import DOMAIN
from .coordinator import CraftyDataCoordinator

class CraftyServiceEntity(CoordinatorEntity[CraftyDataCoordinator], Entity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._host = config_entry.data[CONF_HOST]
        self._port = config_entry.data[CONF_PORT]

        self._name = f'{config_entry.data[CONF_NAME].capitalize()} Service' if config_entry.data[CONF_NAME] else "Service"
        self._unique_id = f'{self._host}_{self._port}_crafty_service'
        self._model = "Crafty Service"
        self._manufacturer = "Crafty Controller"

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def device_info(self) -> Dict[str, Any]:
        return {
            "identifiers": {(DOMAIN, self._unique_id)},
            "name": self._name,
            "model": self._model,
            "manufacturer": self._manufacturer,
        }

class CraftySensorEntity(CoordinatorEntity[CraftyDataCoordinator], SensorEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._host = config_entry.data[CONF_HOST]
        self._port = config_entry.data[CONF_PORT]

        self._name = lambda x: f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller'
        self._device_name = ""
        self._model = ""
        self._state = lambda x: None
        self._attrs = lambda x: {}
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller'
        self._unit = None
        self._native_value = None
        self._icon = None
        self._attr_entity_category = None
        self.entity_id = f'sensor.{self._name}'.lower().replace(" ", "_")

        self._manufacturer = "Crafty Controller"
        self._identifiers = lambda x: f'{x._host}_{x._port}_Crafty_Controller_{x._device_name}_{x._model}'
        self._via_device = None
        self._entry_type = None


    @property
    def name(self) -> str:
        if callable(self._name):
            return self._name(self._coordinator.data)
        return self._name

    @property
    def unique_id(self) -> str:
        if callable(self._unique_id):
            return self._unique_id(self._coordinator.data)
        return self._unique_id

    @property
    def icon(self):
        if callable(self._icon):
            return self._icon(self._coordinator.data)
        return self._icon

    @property
    def unit_of_measurement(self):
        if callable(self._unit):
            return self._unit(self._coordinator.data)
        return self._unit

    @property
    def native_value(self):
        if callable(self._native_value):
            return self._native_value(self._coordinator.data)
        return self._native_value

    @property
    def state(self) -> Optional[str]:
        if callable(self._state):
            if type(self._state(self._coordinator.data)) == str:
                return self._state(self._coordinator.data) if len(self._state(self._coordinator.data)) != 0 else None
            return self._state(self._coordinator.data)
        return self._state if len(self._state) != 0 else None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        if callable(self._attrs):
            return self._attrs(self._coordinator.data)
        return self._attrs

    @property
    def device_info(self) -> Dict[str, Any]:
        info = {
            "name": self._device_name,
            "model": self._model,
            "manufacturer": self._manufacturer,
            "identifiers": {(DOMAIN, self._identifiers(self))},
        }
        if self._via_device is not None:
            info["via_device"] = (DOMAIN, self._via_device)
        if self._entry_type is not None:
            info["entry_type"] = self._entry_type
        return info

class CraftyButtonEntity(CoordinatorEntity[CraftyDataCoordinator], ButtonEntity):
    def __init__(self, coordinator: CraftyDataCoordinator, config_entry: ConfigEntry, hass: HomeAssistant):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._host = config_entry.data[CONF_HOST]
        self._port = config_entry.data[CONF_PORT]
        self._hass = hass

        self._name = lambda x: f'{config_entry.data[CONF_NAME].capitalize() + " " if len(config_entry.data[CONF_NAME]) > 0 else ""}Crafty Controller'
        self._device_name = ""
        self._model = ""
        self._unique_id = f'{self._host}_{self._port}_Crafty_Controller'
        self._icon = None
        self._attr_entity_category = None
        self.entity_id = f'sensor.{self._name}'.lower().replace(" ", "_")
        self._action = lambda x: None
        self._manufacturer = "Crafty Controller"
        self._identifiers = lambda x: f'{x._host}_{x._port}_Crafty_Controller_{x._device_name}_{x._model}'

        self._via_device = None
        self._entry_type = None

    @property
    def name(self) -> str:
        #Return the name of the sensor.#
        return self._name(self._coordinator.data)

    @property
    def unique_id(self) -> str:
        #Return the unique ID of the sensor.#
        return self._unique_id

    @property
    def icon(self):
        return self._icon

    @property
    def device_info(self) -> Dict[str, Any]:
        info = {
            "name": self._device_name,
            "model": self._model,
            "manufacturer": self._manufacturer,
            "identifiers": {(DOMAIN, self._identifiers(self))},
        }
        if self._via_device is not None:
            info["via_device"] = (DOMAIN, self._via_device)
        if self._entry_type is not None:
            info["entry_type"] = self._entry_type
        return info

    async def async_press(self) -> None:
        #Press the button.#
        await self._action(self._coordinator.data.get("client"))