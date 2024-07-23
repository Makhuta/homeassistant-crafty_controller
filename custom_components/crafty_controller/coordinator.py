from datetime import timedelta
import logging
from typing import Dict, Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError

from .const import DOMAIN
from crafty_controller_api import Crafty, FailedToLogin

_LOGGER = logging.getLogger(__name__)

def filter_dict(d: dict, items: list):
    output = {}
    for key, value in d.items():
        if key in items:
            continue
        output[key] = value
    return output

class CraftyDataCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, client: Crafty):
        self._client = client

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_method=self._async_update_data,
            update_interval=timedelta(minutes=10),
        )
    
    async def _async_update_data(self) -> Dict[str, Any]:
        try:
            data = {
                "client": self._client
            }
            items = {
                "roles": self.get_roles,
                "servers": self.get_servers,
                "users": self.get_users,
            }
            
            for key, value in items.items():
                try:
                    data[key] = await value()
                except Exception as e:
                    _LOGGER.warn(e)
                    pass
            return data
        except FailedToLogin as err:
            raise ConfigEntryError("Failed to Log-in") from err
        except Exception as err:
            raise ConfigEntryError("Crafty encoutered unknown") from err

    async def get_roles(self):
        roles = []
        try:
            for role in await self.hass.async_add_executor_job(self._client.roles):
                id = role.get("role_id")
                if id is None:
                    continue
                data = {
                    **role,
                    "servers": await self.hass.async_add_executor_job(self._client.role_servers, id),
                    "users": await self.hass.async_add_executor_job(self._client.role_users, id),
                    }
                roles.append(data)
        except:
            pass
        return roles

    async def get_servers(self):
        servers = []
        try:
            for server in await self.hass.async_add_executor_job(self._client.servers):
                id = server.get("server_id")
                if id is None:
                    continue
                stats = await self.hass.async_add_executor_job(self._client.server_stats, id)
                data = {
                    **server,
                    **(filter_dict(stats, ["server_id"])),
                    **(stats.get("server_id", {})),
                    "accesses": await self.hass.async_add_executor_job(self._client.server_accesses, id),
                    "webhooks": await self.hass.async_add_executor_job(self._client.server_webhooks, id),
                    }
                servers.append(data)
        except:
            pass
        return servers

    async def get_users(self):
        users = []
        try:
            for user in await self.hass.async_add_executor_job(self._client.users):
                id = user.get("user_id")
                if id is None:
                    continue
                data = {
                    **user,
                    **(await self.hass.async_add_executor_job(self._client.user, id)),
                    "picture": await self.hass.async_add_executor_job(self._client.user_picture, id),
                    }
                users.append(data)
        except:
            pass
        return users