"""Number platform for Aohai HaiPower / Sandisolar integration."""
import logging
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AohaiDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# List of parameter definitions matching Sandisolar SD-PRO-EU 6.5K User Manual
NUMBER_CONFIGS = [
    # ---------------- Battery Charging Currents ----------------
    {
        "key": "max_battery_charge_current",
        "name": "Maximum Battery Charging Current",
        "param": "intchargecurrentlimit",
        "min": 1.0,
        "max": 120.0,
        "step": 1.0,
        "unit": UnitOfElectricCurrent.AMPERE,
        "icon": "mdi:battery-charging-high",
        "scale": 100.0,
    },
    {
        "key": "ac_charging_current_limit",
        "name": "AC Battery Charging Current Limit",
        "param": "acChargingCurrent",
        "min": 1.0,
        "max": 100.0,
        "step": 1.0,
        "unit": UnitOfElectricCurrent.AMPERE,
        "icon": "mdi:current-ac",
        "scale": 10.0,
    },
    {
        "key": "generator_charging_current_limit",
        "name": "Generator Charging Current Limit",
        "param": "genChargeLimit",
        "min": 1.0,
        "max": 120.0,
        "step": 1.0,
        "unit": UnitOfElectricCurrent.AMPERE,
        "icon": "mdi:generator-portable",
        "scale": 100.0,
    },

    # ---------------- Battery Voltages ----------------
    {
        "key": "vbat_constant_charge",
        "name": "Battery Charging CV Voltage",
        "param": "vbatconstantcharge",
        "min": 48.0,
        "max": 59.2,
        "step": 0.1,
        "unit": UnitOfElectricPotential.VOLT,
        "icon": "mdi:battery-plus",
        "scale": 100.0,
    },
    {
        "key": "vbat_floating_charge",
        "name": "Float Charging Voltage",
        "param": "uwFloatVLead100T",
        "min": 48.0,
        "max": 58.4,
        "step": 0.1,
        "unit": UnitOfElectricPotential.VOLT,
        "icon": "mdi:battery-clock",
        "scale": 100.0,
    },
    {
        "key": "bat2ac_volt",
        "name": "Battery-to-Grid Voltage (SBU switch to grid)",
        "param": "bat2acVolt",
        "min": 44.0,
        "max": 52.0,
        "step": 0.5,
        "unit": UnitOfElectricPotential.VOLT,
        "icon": "mdi:transmission-tower",
        "scale": 10.0,
    },
    {
        "key": "ac2bat_volt",
        "name": "Grid-to-Battery Voltage (SBU switch to inverter)",
        "param": "ac2batVolt",
        "min": 48.0,
        "max": 58.0,
        "step": 0.5,
        "unit": UnitOfElectricPotential.VOLT,
        "icon": "mdi:battery-arrow-up",
        "scale": 10.0,
    },
    {
        "key": "vbat_stop_discharge",
        "name": "Battery Low-Voltage Shutdown Voltage",
        "param": "vbatStopForDischarge",
        "min": 40.0,
        "max": 48.0,
        "step": 0.5,
        "unit": UnitOfElectricPotential.VOLT,
        "icon": "mdi:battery-alert",
        "scale": 100.0,
    },
    {
        "key": "bat_undervolt_alarm",
        "name": "Battery Under-Voltage Alarm Threshold",
        "param": "batUnderVoltPoint",
        "min": 40.0,
        "max": 50.0,
        "step": 0.5,
        "unit": UnitOfElectricPotential.VOLT,
        "icon": "mdi:bell-alert",
        "scale": 10.0,
    },
    {
        "key": "bat_lv_restart_volt",
        "name": "Low-Voltage Recovery Threshold",
        "param": "batLVBreakRestartVolt",
        "min": 50.0,
        "max": 58.0,
        "step": 0.5,
        "unit": UnitOfElectricPotential.VOLT,
        "icon": "mdi:battery-sync",
        "scale": 10.0,
    },
    {
        "key": "bat_need_charge_volt",
        "name": "Battery Recharging Recovery Threshold",
        "param": "batNeedChrVolt",
        "min": 50.0,
        "max": 56.0,
        "step": 0.5,
        "unit": UnitOfElectricPotential.VOLT,
        "icon": "mdi:battery-charging-wireless",
        "scale": 10.0,
    },
    {
        "key": "bat_overvolt_disconnect",
        "name": "Battery Over-Voltage Disconnect Point",
        "param": "batHighVoltDisConPoint",
        "min": 50.0,
        "max": 62.0,
        "step": 0.5,
        "unit": UnitOfElectricPotential.VOLT,
        "icon": "mdi:flash-alert",
        "scale": 10.0,
    },

    # ---------------- Battery SOC Thresholds ----------------
    {
        "key": "grid_first_stop_soc",
        "name": "On-Grid Discharge Cutoff SOC",
        "param": "gridFirstStopSOC",
        "min": 10.0,
        "max": 90.0,
        "step": 1.0,
        "unit": PERCENTAGE,
        "icon": "mdi:battery-low",
        "scale": 1.0,
    },
    {
        "key": "grid_recover_soc",
        "name": "On-Grid End-of-Discharge Recovery SOC",
        "param": "ubOPRecoverDischargeSOC",
        "min": 20.0,
        "max": 100.0,
        "step": 1.0,
        "unit": PERCENTAGE,
        "icon": "mdi:battery-medium",
        "scale": 1.0,
    },
    {
        "key": "offline_stop_soc",
        "name": "Off-Grid Discharge Cutoff SOC",
        "param": "offLineLoadFirstStopSoc",
        "min": 5.0,
        "max": 90.0,
        "step": 1.0,
        "unit": PERCENTAGE,
        "icon": "mdi:battery-arrow-down-outline",
        "scale": 1.0,
    },
    {
        "key": "offline_recover_soc",
        "name": "Off-Grid End-of-Discharge Recovery SOC",
        "param": "ubOffGridRecoverDischargeSOC",
        "min": 10.0,
        "max": 100.0,
        "step": 1.0,
        "unit": PERCENTAGE,
        "icon": "mdi:battery-charging-outline",
        "scale": 1.0,
    },
    {
        "key": "charging_cutoff_soc",
        "name": "Charging Cut-off SOC",
        "param": "batFirststopSOC",
        "min": 50.0,
        "max": 100.0,
        "step": 1.0,
        "unit": PERCENTAGE,
        "icon": "mdi:battery-check",
        "scale": 1.0,
    },

    # ---------------- Secondary / Smart Load Settings ----------------
    {
        "key": "smart_load_cutoff_soc",
        "name": "Non-Critical Load Disconnection BAT SOC",
        "param": "ubSecondLoadDisConSOC",
        "min": 10.0,
        "max": 100.0,
        "step": 1.0,
        "unit": PERCENTAGE,
        "icon": "mdi:power-plug-off",
        "scale": 1.0,
    },
    {
        "key": "smart_load_cutoff_volt",
        "name": "Non-Critical Load Disconnection BAT Voltage",
        "param": "nonCriticlLoad_BatDisConVolt",
        "min": 42.0,
        "max": 54.0,
        "step": 0.5,
        "unit": UnitOfElectricPotential.VOLT,
        "icon": "mdi:battery-remove",
        "scale": 10.0,
    },
    {
        "key": "smart_load_recover_soc",
        "name": "Non-Critical Load Recovery BAT SOC",
        "param": "nonCriticlLoadRecorveSOC",
        "min": 10.0,
        "max": 100.0,
        "step": 1.0,
        "unit": PERCENTAGE,
        "icon": "mdi:power-plug",
        "scale": 1.0,
    },
    {
        "key": "smart_load_recover_volt",
        "name": "Non-Critical Load Recovery BAT Voltage",
        "param": "nonCriticlLoadRecorveVol",
        "min": 42.0,
        "max": 56.0,
        "step": 0.5,
        "unit": UnitOfElectricPotential.VOLT,
        "icon": "mdi:battery-plus-variant",
        "scale": 10.0,
    },

    # ---------------- Grid & Inverter Power ----------------
    {
        "key": "grid_power_compensation",
        "name": "Anti-Reverse Mains Power Compensation",
        "param": "uwGridPowerCompensation",
        "min": 0.0,
        "max": 300.0,
        "step": 5.0,
        "unit": UnitOfPower.WATT,
        "icon": "mdi:tune",
        "scale": 1.0,
    },
    {
        "key": "active_power_rate",
        "name": "Active Power Rate Limit",
        "param": "activePRate",
        "min": 1.0,
        "max": 100.0,
        "step": 1.0,
        "unit": PERCENTAGE,
        "icon": "mdi:gauge",
        "scale": 1.0,
    },
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Aohai numbers based on a config entry."""
    coordinator: AohaiDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [AohaiGenericNumberEntity(coordinator, conf) for conf in NUMBER_CONFIGS]
    async_add_entities(entities)


class AohaiGenericNumberEntity(CoordinatorEntity[AohaiDataUpdateCoordinator], NumberEntity):
    """Generic number entity for Sandisolar / Aohai inverter settings."""

    _attr_has_entity_name = True
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator: AohaiDataUpdateCoordinator, conf: dict) -> None:
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._conf = conf
        self._param = conf["param"]
        self._scale = conf.get("scale", 1.0)
        self._attr_unique_id = f"{coordinator.dsn}_{conf['key']}"
        self._attr_name = conf["name"]
        self._attr_native_min_value = conf["min"]
        self._attr_native_max_value = conf["max"]
        self._attr_native_step = conf["step"]
        self._attr_native_unit_of_measurement = conf["unit"]
        self._attr_icon = conf.get("icon", "mdi:tune")

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
    def native_value(self) -> float | None:
        """Return the current setting value."""
        if not self.coordinator.data:
            return None
        raw = self.coordinator.data.get("params", {}).get(self._param)
        if raw is not None:
            try:
                return float(raw) / self._scale
            except (ValueError, TypeError):
                return None
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Send setting update command to the inverter via cloud API."""
        raw_val = int(round(value * self._scale))
        _LOGGER.info("Setting %s to %s (raw parameter %s=%s)", self._attr_name, value, self._param, raw_val)
        await self.coordinator.async_set_parameter([f"{self._param}={raw_val}"])
