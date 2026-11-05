"""Config flow for Aohai HaiPower / Sandisolar integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_DSN,
    CONF_CSN,
    CONF_DEVICE_NAME,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)
from .api import AohaiApiClient, AohaiAuthError, AohaiApiError

_LOGGER = logging.getLogger(__name__)

class AohaiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Aohai HaiPower."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._username = None
        self._password = None
        self._devices = []
        self._client = None

    async def async_step_user(self, user_input=None):
        """Handle the initial user login step."""
        errors = {}

        if user_input is not None:
            self._username = user_input[CONF_USERNAME]
            self._password = user_input[CONF_PASSWORD]

            self._client = AohaiApiClient(self._username, self._password)

            try:
                await self.hass.async_add_executor_job(self._client.login)
                self._devices = await self.hass.async_add_executor_job(self._client.get_devices)
            except AohaiAuthError:
                errors["base"] = "invalid_auth"
            except AohaiApiError:
                errors["base"] = "cannot_connect"
            except Exception as ex:
                _LOGGER.exception("Unexpected error during login: %s", ex)
                errors["base"] = "unknown"

            if not errors:
                if not self._devices:
                    errors["base"] = "no_devices_found"
                else:
                    return await self.async_step_device()

        schema = vol.Schema({
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_device(self, user_input=None):
        """Handle device selection and custom naming."""
        errors = {}

        if user_input is not None:
            selected_dsn = user_input[CONF_DSN]
            custom_name = user_input.get(CONF_DEVICE_NAME) or f"Inverter {selected_dsn}"
            scan_interval = user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

            selected_dev = next((d for d in self._devices if d.get("dsn") == selected_dsn), None)

            if selected_dev:
                csn = selected_dev.get("csn", "")
                addr = selected_dev.get("addr", 1)
                model_name = selected_dev.get("typeName", "SD-PRO-EU 6.5K")

                await self.async_set_unique_id(selected_dsn)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=custom_name,
                    data={
                        CONF_USERNAME: self._username,
                        CONF_PASSWORD: self._password,
                        CONF_DSN: selected_dsn,
                        CONF_CSN: csn,
                        CONF_DEVICE_NAME: custom_name,
                        "model_name": model_name,
                        "addr": addr,
                        CONF_SCAN_INTERVAL: scan_interval,
                    },
                )

        device_options = {
            d.get("dsn"): f"{d.get('typeName', 'Inverter')} (DSN: {d.get('dsn')}, Wi-Fi: {d.get('csn', 'None')})"
            for d in self._devices
        }

        # Pick default DSN and default name
        default_dsn = self._devices[0].get("dsn") if self._devices else ""
        default_model = self._devices[0].get("typeName", "Sandisolar SD-PRO-EU 6.5K") if self._devices else "Sandisolar"
        default_title = f"{default_model} ({default_dsn})" if default_dsn else "Sandisolar Inverter"

        schema = vol.Schema({
            vol.Required(CONF_DSN, default=default_dsn): vol.In(device_options),
            vol.Required(CONF_DEVICE_NAME, default=default_title): str,
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                vol.Coerce(int), vol.Clamp(min=10, max=300)
            ),
        })

        return self.async_show_form(step_id="device", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow handler."""
        return AohaiOptionsFlowHandler(config_entry)


class AohaiOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Aohai integration."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        )

        schema = vol.Schema({
            vol.Optional(CONF_SCAN_INTERVAL, default=current_interval): vol.All(
                vol.Coerce(int), vol.Clamp(min=10, max=300)
            ),
        })

        return self.async_show_form(step_id="init", data_schema=schema)
