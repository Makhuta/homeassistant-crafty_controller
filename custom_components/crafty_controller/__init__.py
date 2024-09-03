from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_HOST,
    CONF_PORT,
    CONF_SSL
    )
from crafty_controller_api import FailedToLogin

from .const import DOMAIN, CONF_VERIFY_SSL
from .coordinator import CraftyDataCoordinator
from .helpers import setup_client

PLATFORMS = [
    Platform.SENSOR,
    Platform.BUTTON,
]

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    try:
        clients = await hass.async_add_executor_job(
            setup_client,
            config_entry.data[CONF_USERNAME],
            config_entry.data[CONF_PASSWORD],
            config_entry.data[CONF_HOST],
            config_entry.data[CONF_PORT],
            config_entry.data[CONF_SSL],
            config_entry.data[CONF_VERIFY_SSL],
        )
    except FailedToLogin as err:
        raise ConfigEntryNotReady("Failed to Log-in") from err
    coordinator = CraftyDataCoordinator(hass, clients)

    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload Crafty config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    ):
        del hass.data[DOMAIN][config_entry.entry_id]
        if not hass.data[DOMAIN]:
            del hass.data[DOMAIN]
    return unload_ok