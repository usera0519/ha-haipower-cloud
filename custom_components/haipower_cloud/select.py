"""Select platform for HaiPower Cloud / Sandisolar integration."""
import logging
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    POWER_PRIORITY_OPTIONS,
    POWER_PRIORITY_TO_VAL,
    VAL_TO_POWER_PRIORITY,
    CHARGING_PRIORITY_OPTIONS,
    CHARGING_PRIORITY_TO_VAL,
    VAL_TO_CHARGING_PRIORITY,
    AC_INPUT_OPTIONS,
    AC_INPUT_TO_VAL,
    VAL_TO_AC_INPUT,
    GEN_MODE_OPTIONS,
    GEN_MODE_TO_VAL,
    VAL_TO_GEN_MODE,
)
from .coordinator import AohaiDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up HaiPower selects based on a config entry."""
    coordinator: AohaiDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        AohaiPowerPrioritySelect(coordinator),
        AohaiChargingPrioritySelect(coordinator),
        AohaiAcInputModeSelect(coordinator),
        AohaiGenPortModeSelect(coordinator),
    ])

class AohaiPowerPrioritySelect(CoordinatorEntity[AohaiDataUpdateCoordinator], SelectEntity):
    """Control power supply priority (SOL / UTI / SBU)."""

    _attr_has_entity_name = True
    _attr_name = "Power Supply Priority"
    _attr_icon = "mdi:transmission-tower-export"
    _attr_options = POWER_PRIORITY_OPTIONS

    def __init__(self, coordinator: AohaiDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.dsn}_power_priority"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.dsn)},
            name=self.coordinator.device_name,
            manufacturer="Sandisolar / Aohai Digital Power",
            model=self.coordinator.model_name,
            serial_number=self.coordinator.dsn,
        )

    @property
    def current_option(self) -> str | None:
        if not self.coordinator.data:
            return None
        val = self.coordinator.data.get("params", {}).get("periodpower")
        if val is None:
            val = self.coordinator.data.get("telemetry", {}).get("periodpower")
        return VAL_TO_POWER_PRIORITY.get(val)

    async def async_select_option(self, option: str) -> None:
        val = POWER_PRIORITY_TO_VAL[option]
        _LOGGER.info("Setting Power Supply Priority to %s (val=%s)", option, val)
        await self.coordinator.async_set_parameter([f"periodpower={val}"])


class AohaiChargingPrioritySelect(CoordinatorEntity[AohaiDataUpdateCoordinator], SelectEntity):
    """Control battery charging priority (CSO / SNU / OSO)."""

    _attr_has_entity_name = True
    _attr_name = "Charging Priority"
    _attr_icon = "mdi:battery-charging-wireless"
    _attr_options = CHARGING_PRIORITY_OPTIONS

    def __init__(self, coordinator: AohaiDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.dsn}_charging_priority"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.dsn)},
            name=self.coordinator.device_name,
            manufacturer="Sandisolar / Aohai Digital Power",
            model=self.coordinator.model_name,
            serial_number=self.coordinator.dsn,
        )

    @property
    def current_option(self) -> str | None:
        if not self.coordinator.data:
            return None
        val = self.coordinator.data.get("params", {}).get("periodcharge")
        return VAL_TO_CHARGING_PRIORITY.get(val)

    async def async_select_option(self, option: str) -> None:
        val = CHARGING_PRIORITY_TO_VAL[option]
        _LOGGER.info("Setting Charging Priority to %s (val=%s)", option, val)
        await self.coordinator.async_set_parameter([f"periodcharge={val}"])


class AohaiAcInputModeSelect(CoordinatorEntity[AohaiDataUpdateCoordinator], SelectEntity):
    """Control AC Input Voltage Range (APL / UPS)."""

    _attr_has_entity_name = True
    _attr_name = "Grid Input Voltage Range"
    _attr_icon = "mdi:sine-wave"
    _attr_options = AC_INPUT_OPTIONS

    def __init__(self, coordinator: AohaiDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.dsn}_ac_input_type"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.dsn)},
            name=self.coordinator.device_name,
            manufacturer="Sandisolar / Aohai Digital Power",
            model=self.coordinator.model_name,
            serial_number=self.coordinator.dsn,
        )

    @property
    def current_option(self) -> str | None:
        if not self.coordinator.data:
            return None
        val = self.coordinator.data.get("params", {}).get("acInputType")
        return VAL_TO_AC_INPUT.get(val)

    async def async_select_option(self, option: str) -> None:
        val = AC_INPUT_TO_VAL[option]
        _LOGGER.info("Setting Grid Input Mode to %s (val=%s)", option, val)
        await self.coordinator.async_set_parameter([f"acInputType={val}"])


class AohaiGenPortModeSelect(CoordinatorEntity[AohaiDataUpdateCoordinator], SelectEntity):
    """Control GEN Port Working Mode (0=Generator, 1=Microinverter, 2=Smart Load)."""

    _attr_has_entity_name = True
    _attr_name = "GEN Port Work Mode"
    _attr_icon = "mdi:generator-portable"
    _attr_options = GEN_MODE_OPTIONS

    def __init__(self, coordinator: AohaiDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.dsn}_gen_port_mode"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.dsn)},
            name=self.coordinator.device_name,
            manufacturer="Sandisolar / Aohai Digital Power",
            model=self.coordinator.model_name,
            serial_number=self.coordinator.dsn,
        )

    @property
    def current_option(self) -> str | None:
        if not self.coordinator.data:
            return None
        val = self.coordinator.data.get("params", {}).get("genMode")
        if val is None:
            val = self.coordinator.data.get("telemetry", {}).get("genMode")
        return VAL_TO_GEN_MODE.get(val)

    async def async_select_option(self, option: str) -> None:
        val = GEN_MODE_TO_VAL[option]
        _LOGGER.info("Setting GEN Port Work Mode to %s (val=%s)", option, val)
        await self.coordinator.async_set_parameter([f"genMode={val}"])
