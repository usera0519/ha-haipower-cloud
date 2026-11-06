"""Button platform for Aohai HaiPower / Sandisolar integration."""
import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CONF_ENTITY_MODE,
    PROFILE_AUTO,
    PROFILE_AO_GSA_PRO,
    PROFILE_HSC_AH_1P,
    PROFILE_FSC_HSA_1P,
    PROFILE_HUA_3P_LV,
    PROFILE_HTA_3P_HV,
    PROFILE_FSF_COMPACT,
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
    """Button to trigger External CT Calibration on inverters with CT clamp inputs."""

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
    """Button to trigger External CT Detection / Check on inverters with CT clamp inputs."""

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
