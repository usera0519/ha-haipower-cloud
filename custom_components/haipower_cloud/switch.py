"""Switch platform for HaiPower Cloud / Sandisolar integration."""
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
        "name": "Inverter Operation (Falownik On/Off)",
        "param": "onOff",
        "alt_param": "inveterOnOff",
        "alt_telemetry_key": "onoff",
        "icon": "mdi:power",
    },
    {
        "key": "buzzer_switch",
        "name": "Buzzer (Sygnalizator dźwiękowy)",
        "param": "dspBeepOnOff",
        "icon": "mdi:volume-high",
    },
    {
        "key": "anti_backflow_switch",
        "name": "Anti-Backflow (Blokada eksportu do sieci - Zero Export)",
        "param": "localAntiBackflowEnable",
        "icon": "mdi:transmission-tower-export",
    },
    {
        "key": "ct_enable",
        "name": "CT Enable (Zewnętrzny przekładnik prądowy CT)",
        "param": "ctMode",
        "icon": "mdi:current-ac",
    },
    {
        "key": "overload_to_bypass",
        "name": "Overload to Bypass (Przełączenie na sieć przy przeciążeniu)",
        "param": "overloadToBypass",
        "icon": "mdi:swap-horizontal-bold",
    },
    {
        "key": "zero_current_enable",
        "name": "Zero Power Output (Całkowite odcięcie wypływu)",
        "param": "zeroCurrentEnable",
        "icon": "mdi:cancel",
    },
    {
        "key": "vfrt_enable",
        "name": "VFRT Enable (Stabilizacja napięciowa VFRT)",
        "param": "vfrtEn",
        "icon": "mdi:sine-wave",
    },
    {
        "key": "generator_dry_contact",
        "name": "Generator Dry Contact (Styk bezpotencjałowy auto-startu)",
        "param": "dryControl",
        "icon": "mdi:electric-switch",
    },
    {
        "key": "ac_charge_enable_switch",
        "name": "AC Grid Charging (Ładowanie baterii z sieci AC)",
        "param": "acchargeEn",
        "alt_param": "ubAcChargeEnable",
        "icon": "mdi:battery-charging-wire",
    },
    {
        "key": "eps_enable_switch",
        "name": "EPS Output (Zasilanie awaryjne wyjścia EPS)",
        "param": "epSEn",
        "icon": "mdi:home-lightning-bolt",
    },
    {
        "key": "bypass_enable_switch",
        "name": "Bypass Mode (Obejście sieciowe Bypass)",
        "param": "bypassEn",
        "icon": "mdi:swap-horizontal",
    },
    {
        "key": "gen_charge_enable_switch",
        "name": "Generator Charging (Ładowanie baterii z agregatu)",
        "param": "genChargeEn",
        "icon": "mdi:generator-portable",
    },
    {
        "key": "equalization_switch",
        "name": "Battery Equalization (Wyrównywanie cel baterii)",
        "param": "equalization",
        "icon": "mdi:battery-sync",
    },
    {
        "key": "force_full_charge_switch",
        "name": "Force Full Charge (Wymuszenie pełnego naładowania 100%)",
        "param": "ubForceChargeEnable",
        "alt_param": "forceFullCharge",
        "icon": "mdi:battery-arrow-up",
    },
    {
        "key": "bluetooth_switch",
        "name": "Bluetooth Broadcast (Rozgłaszanie Bluetooth)",
        "param": "ubBluetoothEn",
        "icon": "mdi:bluetooth",
    },
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up HaiPower switches based on a config entry."""
    coordinator: AohaiDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [AohaiGenericSwitch(coordinator, conf) for conf in SWITCH_CONFIGS]
    async_add_entities(entities)


class AohaiGenericSwitch(CoordinatorEntity[AohaiDataUpdateCoordinator], SwitchEntity):
    """Generic switch entity for Sandisolar / HaiPower inverter settings."""

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
        try:
            return int(val) == 1
        except (ValueError, TypeError):
            return None

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
