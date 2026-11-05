"""Switch platform for Aohai HaiPower / Sandisolar integration."""
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AohaiDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SWITCH_CONFIGS = [
    {
        "key": "power_switch",
        "name": "Inverter Operation (On/Off)",
        "param": "onOff",
        "alt_telemetry_key": "onoff",
        "icon": "mdi:power",
    },
    {
        "key": "buzzer_switch",
        "name": "Audible Buzzer Switch",
        "param": "dspBeepOnOff",
        "icon": "mdi:volume-high",
    },
    {
        "key": "anti_backflow_switch",
        "name": "Anti-Backflow Switch (Zero Export)",
        "param": "localAntiBackflowEnable",
        "icon": "mdi:transmission-tower-export",
    },
    {
        "key": "bluetooth_switch",
        "name": "Bluetooth Broadcast Switch",
        "param": "ubBluetoothEn",
        "icon": "mdi:bluetooth",
    },
    {
        "key": "ac_charge_enable_switch",
        "name": "AC Grid Charging Enablement",
        "param": "acchargeEn",
        "alt_param": "ubAcChargeEnable",
        "icon": "mdi:battery-charging-wire",
    },
    {
        "key": "eps_enable_switch",
        "name": "EPS Backup Output Enable",
        "param": "epSEn",
        "icon": "mdi:home-lightning-bolt",
    },
    {
        "key": "bypass_enable_switch",
        "name": "Bypass Output Enable",
        "param": "bypassEn",
        "icon": "mdi:swap-horizontal",
    },
    {
        "key": "gen_charge_enable_switch",
        "name": "Generator Charging Enable",
        "param": "genChargeEn",
        "icon": "mdi:generator-portable",
    },
    {
        "key": "equalization_switch",
        "name": "Battery Equalization Enable",
        "param": "equalization",
        "icon": "mdi:battery-sync",
    },
    {
        "key": "force_full_charge_switch",
        "name": "Force Full Battery Charging Enable",
        "param": "ubBatteryForceFullChargingEnable",
        "icon": "mdi:battery-arrow-up",
    },
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Aohai switches based on a config entry."""
    coordinator: AohaiDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [AohaiGenericSwitch(coordinator, conf) for conf in SWITCH_CONFIGS]
    async_add_entities(entities)


class AohaiGenericSwitch(CoordinatorEntity[AohaiDataUpdateCoordinator], SwitchEntity):
    """Generic switch entity for Sandisolar / Aohai inverter settings."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: AohaiDataUpdateCoordinator, conf: dict) -> None:
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._conf = conf
        self._param = conf["param"]
        self._alt_param = conf.get("alt_param")
        self._alt_telem = conf.get("alt_telemetry_key")
        self._attr_unique_id = f"{coordinator.dsn}_{conf['key']}"
        self._attr_name = conf["name"]
        self._attr_icon = conf.get("icon", "mdi:toggle-switch")

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
    def is_on(self) -> bool | None:
        if not self.coordinator.data:
            return None
        params = self.coordinator.data.get("params", {})
        val = params.get(self._param)
        if val is None and self._alt_param:
            val = params.get(self._alt_param)
        if val is None and self._alt_telem:
            val = self.coordinator.data.get("telemetry", {}).get(self._alt_telem)
        if val is None:
            return None
        return int(val) == 1

    async def async_turn_on(self, **kwargs) -> None:
        _LOGGER.info("Enabling %s (%s)", self._attr_name, self.coordinator.dsn)
        cmds = [f"{self._param}=1"]
        if self._alt_param:
            cmds.append(f"{self._alt_param}=1")
        await self.coordinator.async_set_parameter(cmds)

    async def async_turn_off(self, **kwargs) -> None:
        _LOGGER.info("Disabling %s (%s)", self._attr_name, self.coordinator.dsn)
        cmds = [f"{self._param}=0"]
        if self._alt_param:
            cmds.append(f"{self._alt_param}=0")
        await self.coordinator.async_set_parameter(cmds)
