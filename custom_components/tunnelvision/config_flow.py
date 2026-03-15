"""Config flow for TunnelVision integration."""

import ssl

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_HOST, CONF_PORT

from .const import CONF_USE_SSL, CONF_VERIFY_SSL, DEFAULT_PORT, DOMAIN


class TunnelVisionConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Handle a config flow for TunnelVision."""

    VERSION = 2

    async def async_step_user(self, user_input=None):
        """Handle the initial step — user enters host/port/api_key."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = user_input[CONF_PORT]
            api_key = user_input.get(CONF_API_KEY, "").strip()
            use_ssl = user_input.get(CONF_USE_SSL, False)
            verify_ssl = user_input.get(CONF_VERIFY_SSL, True)

            if not 1 <= port <= 65535:
                errors["base"] = "invalid_port"
            else:
                # Check for duplicate
                await self.async_set_unique_id(f"{host}:{port}")
                self._abort_if_unique_id_configured()

                # Validate connection
                try:
                    scheme = "https" if use_ssl else "http"
                    url = f"{scheme}://{host}:{port}/api/v1/health"
                    headers = {}
                    if api_key:
                        headers["X-API-Key"] = api_key

                    ssl_context: ssl.SSLContext | bool | None = None
                    if use_ssl and not verify_ssl:
                        ssl_context = False  # aiohttp: False = skip verification

                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            url,
                            headers=headers,
                            timeout=aiohttp.ClientTimeout(total=10),
                            ssl=ssl_context,
                        ) as resp:
                            if resp.status == 401:
                                errors["base"] = "invalid_auth"
                            elif resp.status != 200:
                                errors["base"] = "cannot_connect"
                            else:
                                await resp.json()
                                return self.async_create_entry(
                                    title=f"TunnelVision ({host})",
                                    data={
                                        CONF_HOST: host,
                                        CONF_PORT: port,
                                        CONF_API_KEY: api_key,
                                        CONF_USE_SSL: use_ssl,
                                        CONF_VERIFY_SSL: verify_ssl,
                                    },
                                )
                except (aiohttp.ClientError, TimeoutError):
                    errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): vol.All(
                    int, vol.Range(min=1, max=65535),
                ),
                vol.Optional(CONF_API_KEY, default=""): str,
                vol.Optional(CONF_USE_SSL, default=False): bool,
                vol.Optional(CONF_VERIFY_SSL, default=True): bool,
            }),
            errors=errors,
        )
