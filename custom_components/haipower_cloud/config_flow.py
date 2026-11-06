"""Config flow for HaiPower Cloud / Sandisolar integration."""
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
    CONF_ENTITY_MODE,
    ENTITY_MODE_FULL,
    ENTITY_MODE_BASIC,
)
from .api import AohaiApiClient, AohaiAuthError, AohaiApiError

_LOGGER = logging.getLogger(__name__)

class AohaiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HaiPower Cloud."""

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
        """Handle device selection, entity mode, and custom naming."""
        errors = {}

        if user_input is not None:
            selected_dsn = user_input[CONF_DSN]
            custom_name = user_input.get(CONF_DEVICE_NAME) or f"Inverter {selected_dsn}"
            scan_interval = user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            entity_mode = user_input.get(CONF_ENTITY_MODE, ENTITY_MODE_FULL)

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
                        CONF_ENTITY_MODE: entity_mode,
                    },
                )

        device_options = {
            d.get("dsn"): f"{d.get('typeName', 'Inverter')} (DSN: {d.get('dsn')}, Wi-Fi: {d.get('csn', 'None')})"
            for d in self._devices
        }

        mode_options = {
            ENTITY_MODE_FULL: "Full (All sensors, battery BMS, ETA/AVG analytics, and all controls)",
            ENTITY_MODE_BASIC: "Basic (Essential sensors, Energy Dashboard, and Inverter On/Off switch)",
        }

        default_dsn = self._devices[0].get("dsn") if self._devices else ""
        default_model = self._devices[0].get("typeName", "Sandisolar SD-PRO-EU 6.5K") if self._devices else "Sandisolar"
        default_title = f"{default_model} ({default_dsn})" if default_dsn else "HaiPower Cloud Inverter"

        schema = vol.Schema({
            vol.Required(CONF_DSN, default=default_dsn): vol.In(device_options),
            vol.Required(CONF_DEVICE_NAME, default=default_title): str,
            vol.Required(CONF_ENTITY_MODE, default=ENTITY_MODE_FULL): vol.In(mode_options),
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                vol.Coerce(int), vol.Clamp(min=10, max=300)
            ),
        })

        return self.async_show_form(step_id="device", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow handler without arguments (fixes Home Assistant 500 error)."""
        return AohaiOptionsFlowHandler()


class AohaiOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for HaiPower Cloud integration."""

    async def async_step_init(self, user_input=None):
        """Show options menu allowing selection between settings and cloud diagnostic logs."""
        return self.async_show_menu(
            step_id="init",
            menu_options=["settings", "logs"],
        )

    async def async_step_settings(self, user_input=None):
        """Manage integration settings (Entity Mode and Polling Interval)."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        current_mode = self.config_entry.options.get(
            CONF_ENTITY_MODE,
            self.config_entry.data.get(CONF_ENTITY_MODE, ENTITY_MODE_FULL),
        )

        mode_options = {
            ENTITY_MODE_FULL: "Full (All sensors, battery BMS, ETA/AVG analytics, and all controls)",
            ENTITY_MODE_BASIC: "Basic (Essential sensors, Energy Dashboard, and Inverter On/Off switch)",
        }

        schema = vol.Schema({
            vol.Required(CONF_ENTITY_MODE, default=current_mode): vol.In(mode_options),
            vol.Optional(CONF_SCAN_INTERVAL, default=current_interval): vol.All(
                vol.Coerce(int), vol.Clamp(min=10, max=300)
            ),
        })

        return self.async_show_form(
            step_id="settings",
            data_schema=schema,
        )

    async def async_step_logs(self, user_input=None):
        """View recent cloud diagnostic events."""
        if user_input is not None:
            return self.async_create_entry(title="", data=self.config_entry.options)

        coordinator = self.hass.data.get(DOMAIN, {}).get(self.config_entry.entry_id)
        recent_logs_text = coordinator.get_recent_logs_formatted() if coordinator else "No cloud events recorded yet."

        return self.async_show_form(
            step_id="logs",
            data_schema=vol.Schema({}),
            description_placeholders={"logs": recent_logs_text},
        )
