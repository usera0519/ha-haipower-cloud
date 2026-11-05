"""DataUpdateCoordinator for Aohai HaiPower / Sandisolar integration."""
import logging
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .api import AohaiApiClient, AohaiApiError

_LOGGER = logging.getLogger(__name__)

class AohaiDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Aohai inverter data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: AohaiApiClient,
        dsn: str,
        csn: str,
        device_name: str,
        model_name: str = "SD-PRO-EU 6.5K",
        addr: int = 1,
        scan_interval: int = DEFAULT_SCAN_INTERVAL
    ):
        """Initialize the coordinator."""
        self.client = client
        self.dsn = dsn
        self.csn = csn
        self.device_name = device_name
        self.model_name = model_name
        self.addr = addr
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"{device_name} ({dsn})",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self):
        """Fetch real-time data, detailed info, and settings from Aohai API."""
        try:
            device_info = await self.hass.async_add_executor_job(
                self.client.get_device_info, self.dsn
            )
            params_info = await self.hass.async_add_executor_job(
                self.client.get_params_info, self.dsn
            )
            detailed_info = await self.hass.async_add_executor_job(
                self.client.get_detailed_info, self.dsn
            )

            return {
                "telemetry": device_info,
                "params": params_info,
                "details": detailed_info,
            }
        except AohaiApiError as err:
            raise UpdateFailed(f"Error communicating with Aohai API: {err}") from err

    async def async_set_parameter(self, key_value_list: list[str]) -> bool:
        """Send command to update inverter parameters and refresh local state."""
        success = await self.hass.async_add_executor_job(
            self.client.set_parameter, self.csn, self.dsn, self.addr, key_value_list
        )
        if success:
            await self.async_request_refresh()
        return success
