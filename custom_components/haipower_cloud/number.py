"""Number platform for HaiPower Cloud / Sandisolar integration."""
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

# List of parameter definitions matching Sandisolar SD-PRO-EU / HaiPower Cloud API
NUMBER_CONFIGS = [
    # ---------------- Battery Charging Currents ----------------
    {
        "key": "max_battery_charge_current",
        "name": "Max Battery Charge Current (Maks. prąd ładowania baterii)",
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
        "name": "AC Grid Charge Current (Limit prądu ładowania z sieci AC)",
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
        "name": "Generator Charge Current (Limit ładowania z agregatu)",
        "param": "genChargeLimit",
        "min": 1.0,
        "max": 120.0,
        "step": 1.0,
        "unit": UnitOfElectricCurrent.AMPERE,
        "icon": "mdi:generator-portable",
        "scale": 100.0,
    },
    {
        "key": "generator_input_power",
        "name": "Generator Rated Power (Moc wejściowa agregatu)",
        "param": "genInputPower",
        "min": 100.0,
        "max": 10000.0,
        "step": 50.0,
        "unit": UnitOfPower.WATT,
        "icon": "mdi:engine",
        "scale": 1.0,
    },
    {
        "key": "ct_current_ratio",
        "name": "CT Current Ratio (Przekładnia przekładnika prądowego 1~3000)",
        "param": "ctRatio",
        "min": 1.0,
        "max": 3000.0,
        "step": 1.0,
        "unit": "",
        "icon": "mdi:numeric",
        "scale": 1.0,
    },

    # ---------------- Battery Voltages ----------------
    {
        "key": "vbat_constant_charge",
        "name": "Battery Charging CV Voltage (Napięcie absorpcji CV)",
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
        "name": "Battery Float Voltage (Napięcie podtrzymujące Float)",
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
        "name": "Battery to Grid Voltage (SBU: Przełączenie na sieć przy U)",
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
        "name": "Grid to Battery Voltage (SBU: Powrót do inwertera przy U)",
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
        "name": "Battery Low-Voltage Cutoff (Napięcie odcięcia rozładowania)",
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
        "name": "Battery Under-Voltage Alarm (Alarm niskiego napięcia baterii)",
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
        "name": "Low-Voltage Recovery (Napięcie restartu po rozładowaniu)",
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
        "name": "Battery Recharge Threshold (Napięcie wymuszenia doładowania)",
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
        "name": "Over-Voltage Disconnect (Odłączenie przy przepięciu baterii)",
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
        "name": "On-Grid Discharge Cutoff SOC (Odcięcie rozładowania sieciowego SOC)",
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
        "name": "On-Grid Recovery SOC (Powrót do rozładowania sieciowego SOC)",
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
        "name": "Off-Grid Discharge Cutoff SOC (Odcięcie rozładowania wyspowego SOC)",
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
        "name": "Off-Grid Recovery SOC (Powrót do rozładowania wyspowego SOC)",
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
        "name": "Charging Cutoff SOC (Próg zakończenia ładowania baterii SOC)",
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
        "name": "Smart Load Cutoff SOC (Odłączenie odbiorników niekrytycznych SOC)",
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
        "name": "Smart Load Cutoff Voltage (Odłączenie odbiorników niekrytycznych U)",
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
        "name": "Smart Load Recovery SOC (Ponowne załączenie odbiorników niekrytycznych SOC)",
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
        "name": "Smart Load Recovery Voltage (Ponowne załączenie odbiorników niekrytycznych U)",
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
        "name": "Anti-Reverse Grid Compensation (Kompensacja mocy zerowego eksportu)",
        "param": "uwGridPowerCompensation",
        "min": 0.0,
        "max": 500.0,
        "step": 5.0,
        "unit": UnitOfPower.WATT,
        "icon": "mdi:tune",
        "scale": 1.0,
    },
    {
        "key": "active_power_rate",
        "name": "Active Power Rate Limit (Limit mocy czynnej falownika %)",
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
    """Set up HaiPower numbers based on a config entry."""
    coordinator: AohaiDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [AohaiGenericNumberEntity(coordinator, conf) for conf in NUMBER_CONFIGS]
    async_add_entities(entities)


class AohaiGenericNumberEntity(CoordinatorEntity[AohaiDataUpdateCoordinator], NumberEntity):
    """Generic number entity for Sandisolar / HaiPower inverter settings."""

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
        unit = conf["unit"]
        self._attr_native_unit_of_measurement = unit if unit != "" else None
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
