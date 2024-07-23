from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigEntry
from homeassistant.core import callback
from homeassistant.const import (
    CONF_NAME,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_HOST,
    CONF_PORT,
    CONF_SSL
    )
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    ConstantSelector,
    ConstantSelectorConfig
)
from .const import (
    DOMAIN,
    DEFAULT_NAME
)
from .helpers import setup_client
from crafty_controller_api import FailedToLogin

SCHEMA = vol.Schema({
    vol.Optional(CONF_NAME, default=""): vol.All(str),
    vol.Required(CONF_USERNAME): vol.All(str),
    vol.Required(CONF_PASSWORD): vol.All(str),
    vol.Required(CONF_HOST, default="localhost"): vol.All(str),
    vol.Required(CONF_PORT, default=8443): vol.All(vol.Coerce(int), vol.Range(min=0)),
    vol.Required(CONF_SSL, default=True): vol.All(bool),
})


class CraftyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for the Crafty integration."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ):
        errors = {}

        if user_input is not None:
            self._async_abort_entries_match({CONF_HOST: user_input[CONF_HOST], CONF_PORT: user_input[CONF_PORT]})
            try:
                await self.hass.async_add_executor_job(
                    setup_client,
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    user_input[CONF_HOST],
                    user_input[CONF_PORT],
                    user_input[CONF_SSL],
                )
            except FailedToLogin as err:
                errors = {'base': 'failed_to_login'}
            else:
                return self.async_create_entry(title=user_input[CONF_NAME] if len(user_input[CONF_NAME]) > 0 else DEFAULT_NAME, data=user_input)

        schema = self.add_suggested_values_to_schema(SCHEMA, user_input)
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)