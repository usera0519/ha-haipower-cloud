"""Button platform for Aohai HaiPower / Sandisolar integration."""
import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import AohaiApiError

from .const import (
    DOMAIN,
    CONF_ENTITY_MODE,
    PROFILE_AUTO,
    PROFILE_HSC_AH_1P,
    PROFILE_FSC_HSA_1P,
    PROFILE_READ_ONLY,
    PROFILE_FULL,
    get_effective_profile,
)
from .coordinator import AohaiDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Aohai buttons based on model profile."""
    coordinator: AohaiDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    cfg_profile = entry.options.get(CONF_ENTITY_MODE, entry.data.get(CONF_ENTITY_MODE, PROFILE_AUTO))
    effective_profile = get_effective_profile(cfg_profile, coordinator.model_name)

    if effective_profile == PROFILE_READ_ONLY:
        _LOGGER.info("Skipping button entities for %s in read-only mode", coordinator.dsn)
        return

    buttons = [AohaiRefreshButton(coordinator)]

    # CT Calibration and Detection buttons are applicable to inverters with physical CT clamp inputs
    # (AO-6KSL-G3 uses RS485 Smart Meter instead of physical CT clamp, so CT buttons are excluded in its profile)
    if effective_profile in (PROFILE_HSC_AH_1P, PROFILE_FSC_HSA_1P, PROFILE_FULL):
        buttons.append(AohaiCtCalibrationButton(coordinator))
        buttons.append(AohaiCtDetectionButton(coordinator))
        _LOGGER.info("Registered CT Calibration and Detection buttons for %s (%s)", coordinator.dsn, effective_profile)
    else:
        _LOGGER.info("Excluding physical CT clamp buttons for %s (profile: %s, uses Smart Meter or compact)", coordinator.dsn, effective_profile)

    async_add_entities(buttons)


class AohaiBaseButton(CoordinatorEntity[AohaiDataUpdateCoordinator], ButtonEntity):
    """Base button entity for HaiPower Cloud."""

    _attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.dsn)},
            name=self.coordinator.device_name,
            manufacturer="Sandisolar / Aohai Digital Power",
            model=self.coordinator.model_name,
            serial_number=self.coordinator.dsn,
        )

    async def _async_send_register(self, register: int, value: int) -> None:
        """Send a hardware register command wrapped in HomeAssistantError on failure."""
        try:
            await self.coordinator.async_set_register(register, value)
        except AohaiApiError as err:
            raise HomeAssistantError(f"Failed to execute {self._attr_name}: {err}") from err


class AohaiRefreshButton(AohaiBaseButton):
    """Button to force immediate data refresh from inverter."""

    _attr_name = "Force Inverter Data Refresh"
    _attr_icon = "mdi:refresh"

    def __init__(self, coordinator: AohaiDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.dsn}_refresh_button"

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.info("Manually triggering refresh for inverter %s", self.coordinator.dsn)
        await self.coordinator.async_refresh()
        if not self.coordinator.last_update_success and self.coordinator.last_exception:
            raise HomeAssistantError(
                f"Failed to refresh inverter data: {self.coordinator.last_exception}"
            ) from self.coordinator.last_exception


class AohaiCtCalibrationButton(AohaiBaseButton):
    """Button to trigger External CT Calibration on inverters with CT clamp inputs."""

    _attr_name = "CT Calibration"
    _attr_icon = "mdi:tune"

    def __init__(self, coordinator: AohaiDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.dsn}_ct_calibration"

    async def async_press(self) -> None:
        """Trigger CT Calibration command (register 96=1)."""
        _LOGGER.info("Triggering CT Calibration for inverter %s", self.coordinator.dsn)
        await self._async_send_register(96, 1)


class AohaiCtDetectionButton(AohaiBaseButton):
    """Button to trigger External CT Detection / Check on inverters with CT clamp inputs."""

    _attr_name = "CT Detection"
    _attr_icon = "mdi:magnify-scan"

    def __init__(self, coordinator: AohaiDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.dsn}_ct_detection"

    async def async_press(self) -> None:
        """Trigger CT Detection command (register 96=2)."""
        _LOGGER.info("Triggering CT Detection for inverter %s", self.coordinator.dsn)
        await self._async_send_register(96, 2)
