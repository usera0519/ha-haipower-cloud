"""Sensor platform for Aohai HaiPower / Sandisolar integration."""
import logging
from dataclasses import dataclass
from typing import Callable, Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfPower,
    UnitOfElectricPotential,
    UnitOfElectricCurrent,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfTemperature,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    FAULT_CODE_MAP,
    WARN_CODE_MAP,
    BATTERY_TYPE_MAP,
    BATTERY_PRIORITY_MAP,
    OPERATION_MODE_MAP,
)
from .coordinator import AohaiDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

@dataclass
class AohaiSensorEntityDescription(SensorEntityDescription):
    """Class describing Aohai sensor entities."""
    value_fn: Callable[[dict[str, Any]], Any] = None


# Helper lookup functions
def _get_status(data: dict) -> str:
    inv_info = data.get("details", {}).get("invInfo", {})
    return inv_info.get("inverterStatus2") or data.get("telemetry", {}).get("status2") or "Unknown"

def _get_op_mode(data: dict) -> str:
    code = data.get("details", {}).get("invInfo", {}).get("periodpower")
    if code is None:
        code = data.get("params", {}).get("periodpower")
    if code is None:
        code = data.get("telemetry", {}).get("periodpower")
    return OPERATION_MODE_MAP.get(code, f"Mode {code}" if code is not None else "Unknown")

def _get_fault_code(data: dict) -> str:
    inv_info = data.get("details", {}).get("invInfo", {})
    master = inv_info.get("invMainErrorCode", 0)
    slave = inv_info.get("invErrorSubCode", 0)
    return f"{master}/{slave}"

def _get_fault_desc(data: dict) -> str:
    inv_info = data.get("details", {}).get("invInfo", {})
    master = inv_info.get("invMainErrorCode", 0)
    return FAULT_CODE_MAP.get(master, f"Fault Code {master}")

def _get_warn_code(data: dict) -> str:
    inv_info = data.get("details", {}).get("invInfo", {})
    master = inv_info.get("invMainWarnCode", 0)
    slave = inv_info.get("invWarnSubCode", 0)
    return f"{master}/{slave}"

def _get_warn_desc(data: dict) -> str:
    inv_info = data.get("details", {}).get("invInfo", {})
    master = inv_info.get("invMainWarnCode", 0)
    return WARN_CODE_MAP.get(master, f"Warning Code {master}")

def _get_battery_type(data: dict) -> str:
    btype = data.get("details", {}).get("invData", {}).get("batteryType")
    if btype is None:
        btype = data.get("telemetry", {}).get("batteryType")
    return BATTERY_TYPE_MAP.get(btype, f"Type {btype}" if btype is not None else "Unknown")

def _get_battery_priority(data: dict) -> str:
    p = data.get("details", {}).get("invData", {}).get("priority")
    return BATTERY_PRIORITY_MAP.get(p, f"Priority {p}" if p is not None else "Load Priority")

def _get_battery_status(data: dict) -> str:
    inv_data = data.get("details", {}).get("invData", {})
    pcharge = inv_data.get("pcharge") or data.get("telemetry", {}).get("pcharge", 0.0)
    pdischarge = inv_data.get("pdischarge") or data.get("telemetry", {}).get("pdischarge", 0.0)
    try:
        pcharge_val = float(pcharge)
        pdischarge_val = float(pdischarge)
    except (ValueError, TypeError):
        return "Standby"
    if pcharge_val > 10.0:
        return "Charging"
    if pdischarge_val > 10.0:
        return "Discharging"
    return "Standby"


SENSOR_TYPES: tuple[AohaiSensorEntityDescription, ...] = (
    # ==========================================
    # 1. Real-Time Status & Operating Mode
    # ==========================================
    AohaiSensorEntityDescription(
        key="inverter_status",
        name="Inverter Status",
        icon="mdi:information-outline",
        value_fn=_get_status,
    ),
    AohaiSensorEntityDescription(
        key="operation_mode",
        name="Operation Mode",
        icon="mdi:tune-vertical",
        value_fn=_get_op_mode,
    ),

    # ==========================================
    # 2. Diagnostic Codes & Descriptions
    # ==========================================
    AohaiSensorEntityDescription(
        key="fault_code",
        name="Fault Code (Master/Slave)",
        icon="mdi:alert-circle",
        value_fn=_get_fault_code,
    ),
    AohaiSensorEntityDescription(
        key="fault_description",
        name="Fault Description",
        icon="mdi:alert",
        value_fn=_get_fault_desc,
    ),
    AohaiSensorEntityDescription(
        key="warn_code",
        name="Warn Code (Master/Slave)",
        icon="mdi:alert-box-outline",
        value_fn=_get_warn_code,
    ),
    AohaiSensorEntityDescription(
        key="warn_description",
        name="Warn Description",
        icon="mdi:bell-alert-outline",
        value_fn=_get_warn_desc,
    ),

    # ==========================================
    # 3. Device Basic Information (Detailed Info Tab)
    # ==========================================
    AohaiSensorEntityDescription(
        key="device_serial_number",
        name="Device Serial Number",
        icon="mdi:barcode",
        value_fn=lambda data: data.get("details", {}).get("invInfo", {}).get("dsn") or data.get("telemetry", {}).get("dsn") or "Unknown",
    ),
    AohaiSensorEntityDescription(
        key="data_logger_number",
        name="Data Logger Number",
        icon="mdi:wifi-marker",
        value_fn=lambda data: data.get("details", {}).get("invInfo", {}).get("csn") or data.get("telemetry", {}).get("csn") or "Unknown",
    ),
    AohaiSensorEntityDescription(
        key="device_model",
        name="Device Model",
        icon="mdi:solar-power",
        value_fn=lambda data: data.get("details", {}).get("invInfo", {}).get("deviceType2") or "AO-6KSL-G3",
    ),
    AohaiSensorEntityDescription(
        key="system_time",
        name="System Time",
        icon="mdi:clock-digital",
        value_fn=lambda data: data.get("details", {}).get("invInfo", {}).get("sysTime") or data.get("params", {}).get("sysTime") or "Unknown",
    ),
    AohaiSensorEntityDescription(
        key="hardware_mode_code",
        name="Hardware Mode Code",
        icon="mdi:identifier",
        value_fn=lambda data: data.get("details", {}).get("invInfo", {}).get("module") or "Unknown",
    ),
    AohaiSensorEntityDescription(
        key="arm_version",
        name="ARM Software Version",
        icon="mdi:cpu-32-bit",
        value_fn=lambda data: data.get("details", {}).get("invInfo", {}).get("m3versionName") or "Unknown",
    ),
    AohaiSensorEntityDescription(
        key="dsp_version",
        name="DSP Software Version",
        icon="mdi:chip",
        value_fn=lambda data: data.get("details", {}).get("invInfo", {}).get("fwName") or "Unknown",
    ),
    AohaiSensorEntityDescription(
        key="firmware_version",
        name="Firmware Version",
        icon="mdi:tag-outline",
        value_fn=lambda data: data.get("details", {}).get("invInfo", {}).get("fwversion") or "Unknown",
    ),
    AohaiSensorEntityDescription(
        key="total_work_time",
        name="Total Work Time",
        icon="mdi:timer-outline",
        value_fn=lambda data: data.get("details", {}).get("invInfo", {}).get("timeTotal2") or "Unknown",
    ),

    # ==========================================
    # 4. Battery Detailed Information
    # ==========================================
    AohaiSensorEntityDescription(
        key="battery_type",
        name="Battery Type",
        icon="mdi:battery-heart-variant",
        value_fn=_get_battery_type,
    ),
    AohaiSensorEntityDescription(
        key="battery_priority",
        name="Battery Priority",
        icon="mdi:priority-high",
        value_fn=_get_battery_priority,
    ),
    AohaiSensorEntityDescription(
        key="battery_status",
        name="Battery Status",
        icon="mdi:battery-sync",
        value_fn=_get_battery_status,
    ),
    AohaiSensorEntityDescription(
        key="battery_voltage",
        name="Battery Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("vbat") if data.get("details", {}).get("invData", {}).get("vbat") is not None else data.get("telemetry", {}).get("vbat", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="battery_current",
        name="Battery Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("bmSBatteryCurr") if data.get("details", {}).get("invData", {}).get("bmSBatteryCurr") is not None else data.get("telemetry", {}).get("bmSBatteryCurr", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="battery_max_charge_curr",
        name="Max Charge Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-dc",
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("bmSMaxChargeCurr", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="battery_max_discharge_curr",
        name="Max Discharge Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-dc",
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("bmSMaxDischargeCurr", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="battery_min_cell_voltage",
        name="Min Cell Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-arrow-down",
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("minCellVol", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="battery_max_cell_voltage",
        name="Max Cell Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-arrow-up",
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("maxCellVol", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="battery_temperature",
        name="Battery Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("bmSBatteryTemp", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="battery_rated_capacity",
        name="Rated Capacity",
        native_unit_of_measurement="Ah",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-standard",
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("bmSGaugeFCC", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="battery_charging_voltage",
        name="Charging Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash-outline",
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("bmSConstantVolt", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="battery_module_count",
        name="Number of Battery Module",
        icon="mdi:counter",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("moduleNum", 0),
    ),
    AohaiSensorEntityDescription(
        key="battery_cell_count",
        name="Number of Battery Cells",
        icon="mdi:counter",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("cellNum", 0),
    ),
    AohaiSensorEntityDescription(
        key="battery_soc",
        name="Battery SOC",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("soC") if data.get("details", {}).get("invData", {}).get("soC") is not None else data.get("telemetry", {}).get("soc", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="battery_soh",
        name="Battery SOH",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:battery-heart-variant",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("bmSSOH", 0.0),
    ),

    # ==========================================
    # 5. Real-Time Power Measurements
    # ==========================================
    AohaiSensorEntityDescription(
        key="pv_total_power",
        name="PV Total Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("ppvAll", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="house_load_power",
        name="House Load Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("loadPower", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="eps_output_power",
        name="EPS Backup Load Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("epsPower", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="battery_charging_power",
        name="Battery Charging Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("pcharge", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="battery_discharging_power",
        name="Battery Discharging Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("pdischarge", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="grid_active_power",
        name="Grid Active Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("pactogridtotal", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="extra_ac_power_to_grid",
        name="Grid Export Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("extraACPowertogrid", 0.0),
    ),

    # ==========================================
    # 6. Solar String MPPT Parameters
    # ==========================================
    AohaiSensorEntityDescription(
        key="pv1_voltage",
        name="PV1 Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("vpv1", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="pv1_power",
        name="PV1 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("ppv1", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="pv2_voltage",
        name="PV2 Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("vpv2", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="pv2_power",
        name="PV2 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("ppv2", 0.0),
    ),

    # ==========================================
    # 7. AC Grid & Inverter Electrical Measurements
    # ==========================================
    AohaiSensorEntityDescription(
        key="ac_voltage_phase_r",
        name="Grid Voltage (Phase R)",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("vac1", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="grid_frequency",
        name="Grid Frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("fac", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="dc_bus_voltage",
        name="DC Bus Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("dspBusTotalVolt", 0.0),
    ),

    # ==========================================
    # 8. Home Assistant Energy Dashboard Entities
    # ==========================================
    AohaiSensorEntityDescription(
        key="daily_pv_energy",
        name="Daily PV Generation Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("epVAllToday", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="total_pv_energy",
        name="Total PV Generation Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("epvTotal", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="daily_load_energy",
        name="Daily Load Consumption Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("eloadToday", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="total_load_energy",
        name="Total Load Consumption Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("eloadTotal", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="daily_grid_in_energy",
        name="Daily Grid Energy Import",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("efromGridToday", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="total_grid_in_energy",
        name="Total Grid Energy Import",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("efromGridTotal", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="daily_grid_out_energy",
        name="Daily Grid Energy Export",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("etoGridToday", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="total_grid_out_energy",
        name="Total Grid Energy Export",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("etoGridTotal", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="daily_battery_charge_energy",
        name="Daily Battery Charge Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("echargeToday", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="daily_battery_discharge_energy",
        name="Daily Battery Discharge Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("edischargeToday", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="total_battery_charge_energy",
        name="Total Battery Charge Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("echargeTotal", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="total_battery_discharge_energy",
        name="Total Battery Discharge Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("edischargeTotal", 0.0),
    ),

    # ==========================================
    # 9. Environmental Savings & Timestamp
    # ==========================================
    AohaiSensorEntityDescription(
        key="co2_reduction",
        name="CO2 Reduction Total",
        native_unit_of_measurement="kg",
        icon="mdi:molecule-co2",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("co2Total", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="tree_equivalent",
        name="Equivalent Trees Planted",
        icon="mdi:tree",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("treeTotal", 0.0),
    ),
    AohaiSensorEntityDescription(
        key="last_telemetry_time",
        name="Last Telemetry Timestamp",
        icon="mdi:clock-check-outline",
        value_fn=lambda data: data.get("telemetry", {}).get("lastTime") or "Unknown",
    ),
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Aohai sensors based on a config entry."""
    coordinator: AohaiDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [AohaiSensor(coordinator, description) for description in SENSOR_TYPES]
    async_add_entities(entities)

class AohaiSensor(CoordinatorEntity[AohaiDataUpdateCoordinator], SensorEntity):
    """Representation of an Aohai Inverter sensor."""

    entity_description: AohaiSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(self, coordinator: AohaiDataUpdateCoordinator, description: AohaiSensorEntityDescription) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.dsn}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.dsn)},
            name=self.coordinator.device_name,
            manufacturer="Sandisolar / Aohai Digital Power",
            model=self.coordinator.model_name,
            serial_number=self.coordinator.dsn,
        )

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
