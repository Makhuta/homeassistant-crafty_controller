from typing import Any, Dict, Optional


from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
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
        self._icon = None
        self._attr_entity_category = None
        self.entity_id = f'sensor.{self._name}'.lower().replace(" ", "_")


    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name(self._coordinator.data)

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._unique_id

    @property
    def icon(self):
        return self._icon

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit

    @property
    def state(self) -> Optional[str]:
        """Return the value of the sensor."""
        return self._state(self._coordinator.data)

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return self._attrs(self._coordinator.data)

    @property
    def device_info(self) -> Dict[str, Any]:
        return {
            "name": self._device_name,
            "model": self._model,
            "manufacturer": "Crafty Controller",
            "identifiers": {(DOMAIN, f'{self._host}_{self._port}_Crafty_Controller_{self._device_name}_{self._model}')},
        }

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


    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name(self._coordinator.data)

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._unique_id

    @property
    def icon(self):
        return self._icon

    @property
    def device_info(self) -> Dict[str, Any]:
        return {
            "name": self._device_name,
            "model": self._model,
            "manufacturer": "Crafty Controller",
            "identifiers": {(DOMAIN, f'{self._host}_{self._port}_Crafty_Controller_{self._device_name}_{self._model}')},
        }

    async def async_press(self) -> None:
        """Press the button."""
        await self._action(self._coordinator.data.get("client"))