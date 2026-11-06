"""Button platform for Aohai HaiPower / Sandisolar integration."""
import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AohaiDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Aohai buttons based on a config entry."""
    coordinator: AohaiDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        AohaiRefreshButton(coordinator),
        AohaiCtCalibrationButton(coordinator),
        AohaiCtDetectionButton(coordinator),
    ])

class AohaiRefreshButton(CoordinatorEntity[AohaiDataUpdateCoordinator], ButtonEntity):
    """Button to force immediate data refresh from inverter."""

    _attr_has_entity_name = True
    _attr_name = "Force Inverter Data Refresh"
    _attr_icon = "mdi:refresh"

    def __init__(self, coordinator: AohaiDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.dsn}_refresh_button"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.dsn)},
            name=self.coordinator.device_name,
            manufacturer="Sandisolar / Aohai Digital Power",
            model=self.coordinator.model_name,
            serial_number=self.coordinator.dsn,
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.info("Manually triggering refresh for inverter %s", self.coordinator.dsn)
        await self.coordinator.async_request_refresh()


class AohaiCtCalibrationButton(CoordinatorEntity[AohaiDataUpdateCoordinator], ButtonEntity):
    """Button to trigger External CT Calibration on the inverter."""

    _attr_has_entity_name = True
    _attr_name = "CT Calibration"
    _attr_icon = "mdi:tune"

    def __init__(self, coordinator: AohaiDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.dsn}_ct_calibration"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.dsn)},
            name=self.coordinator.device_name,
            manufacturer="Sandisolar / Aohai Digital Power",
            model=self.coordinator.model_name,
            serial_number=self.coordinator.dsn,
        )

    async def async_press(self) -> None:
        """Trigger CT Calibration command (register 96=1)."""
        _LOGGER.info("Triggering CT Calibration for inverter %s", self.coordinator.dsn)
        await self.coordinator.async_set_register(96, 1)


class AohaiCtDetectionButton(CoordinatorEntity[AohaiDataUpdateCoordinator], ButtonEntity):
    """Button to trigger External CT Detection / Check on the inverter."""

    _attr_has_entity_name = True
    _attr_name = "CT Detection"
    _attr_icon = "mdi:magnify-scan"

    def __init__(self, coordinator: AohaiDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.dsn}_ct_detection"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.dsn)},
            name=self.coordinator.device_name,
            manufacturer="Sandisolar / Aohai Digital Power",
            model=self.coordinator.model_name,
            serial_number=self.coordinator.dsn,
        )

    async def async_press(self) -> None:
        """Trigger CT Detection command (register 96=2)."""
        _LOGGER.info("Triggering CT Detection for inverter %s", self.coordinator.dsn)
        await self.coordinator.async_set_register(96, 2)
