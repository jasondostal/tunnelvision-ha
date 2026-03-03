"""Config flow for TunnelVision integration."""

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_API_KEY

from .const import DOMAIN, DEFAULT_PORT


class TunnelVisionConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TunnelVision."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step — user enters host/port/api_key."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            api_key = user_input.get(CONF_API_KEY, "")

            # Check for duplicate
            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()

            # Validate connection
            try:
                url = f"http://{host}:{port}/api/v1/health"
                headers = {}
                if api_key:
                    headers["X-API-Key"] = api_key

                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        if resp.status == 401:
                            errors["base"] = "invalid_auth"
                        elif resp.status != 200:
                            errors["base"] = "cannot_connect"
                        else:
                            data = await resp.json()
                            return self.async_create_entry(
                                title=f"TunnelVision ({host})",
                                data={
                                    CONF_HOST: host,
                                    CONF_PORT: port,
                                    CONF_API_KEY: api_key,
                                },
                            )
            except (aiohttp.ClientError, TimeoutError):
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Optional(CONF_API_KEY, default=""): str,
            }),
            errors=errors,
        )
