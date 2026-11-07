"""Sensor platform for HaiPower Cloud / Sandisolar integration."""
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
    CONF_ENTITY_MODE,
    PROFILE_AUTO,
    PROFILE_AO_GSA_PRO,
    PROFILE_BASIC,
    PROFILE_FULL,
    get_effective_profile,
)
from .coordinator import AohaiDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

@dataclass
class AohaiSensorEntityDescription(SensorEntityDescription):
    """Class describing Aohai sensor entities."""
    value_fn: Callable[[dict[str, Any]], Any] = None
    extra_attrs_fn: Callable[[dict[str, Any]], dict[str, Any]] = None
    is_basic: bool = False


# Helper lookup functions
def _get_status(data: dict) -> str:
    inv_info = data.get("details", {}).get("invInfo", {})
    return inv_info.get("inverterStatus2") or data.get("telemetry", {}).get("status2") or "Normal"

def _get_op_mode(data: dict) -> str:
    code = data.get("details", {}).get("invInfo", {}).get("periodpower")
    if code is None:
        code = data.get("params", {}).get("periodpower")
    if code is None:
        code = data.get("telemetry", {}).get("periodpower")
    return OPERATION_MODE_MAP.get(code, f"Mode {code}" if code is not None else "Normal")

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
    return BATTERY_TYPE_MAP.get(btype, f"Type {btype}" if btype is not None else "Lithium Battery")

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
    if pcharge_val > 15.0:
        return "Charging"
    if pdischarge_val > 15.0:
        return "Discharging"
    return "Standby"


def _get_work_time_attrs(data: Any) -> dict[str, Any]:
    """Extract numeric work time attributes safely."""
    if hasattr(data, "data"):
        data = data.data
    if not isinstance(data, dict):
        return {}
    time_total = data.get("details", {}).get("invData", {}).get("timeTotal")
    if time_total is not None:
        try:
            val = float(time_total)
            return {
                "total_minutes": int(val),
                "total_hours": round(val / 60.0, 1),
            }
        except (ValueError, TypeError):
            pass
    return {}


SENSOR_TYPES: tuple[AohaiSensorEntityDescription, ...] = (
    # ==========================================
    # 1. Real-Time Status & Operating Mode (BASIC)
    # ==========================================
    AohaiSensorEntityDescription(
        key="inverter_status",
        name="Inverter Status",
        icon="mdi:information-outline",
        value_fn=_get_status,
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="operation_mode",
        name="Operation Mode",
        icon="mdi:tune-vertical",
        value_fn=_get_op_mode,
        is_basic=True,
    ),

    # ==========================================
    # 2. Diagnostic Codes & Descriptions (BASIC)
    # ==========================================
    AohaiSensorEntityDescription(
        key="fault_code",
        name="Fault Code",
        icon="mdi:alert-circle",
        value_fn=_get_fault_code,
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="fault_description",
        name="Fault Description",
        icon="mdi:alert",
        value_fn=_get_fault_desc,
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="warn_code",
        name="Warning Code",
        icon="mdi:alert-box-outline",
        value_fn=_get_warn_code,
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="warn_description",
        name="Warning Description",
        icon="mdi:bell-alert-outline",
        value_fn=_get_warn_desc,
        is_basic=True,
    ),

    # ==========================================
    # 3. Device Basic Information
    # ==========================================
    AohaiSensorEntityDescription(
        key="device_serial_number",
        name="Device Serial Number",
        icon="mdi:barcode",
        value_fn=lambda data: data.get("details", {}).get("invInfo", {}).get("dsn") or data.get("telemetry", {}).get("dsn") or "Unknown",
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="data_logger_number",
        name="Data Logger CSN",
        icon="mdi:wifi",
        value_fn=lambda data: data.get("details", {}).get("invInfo", {}).get("csn") or data.get("telemetry", {}).get("csn") or "Unknown",
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="device_model",
        name="Device Model",
        icon="mdi:solar-power",
        value_fn=lambda data: data.get("details", {}).get("invInfo", {}).get("module") or "SD-PRO-EU 6.5K",
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="system_time",
        name="System Time",
        icon="mdi:clock-outline",
        value_fn=lambda data: data.get("details", {}).get("invInfo", {}).get("sysTime") or data.get("telemetry", {}).get("lastTime") or "Unknown",
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="hardware_mode_code",
        name="Hardware Mode Code",
        icon="mdi:chip",
        value_fn=lambda data: data.get("details", {}).get("invInfo", {}).get("deviceType2", "Unknown"),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="arm_version",
        name="ARM Software Version",
        icon="mdi:memory",
        value_fn=lambda data: data.get("details", {}).get("invInfo", {}).get("m3versionName") or "Unknown",
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="dsp_version",
        name="DSP Software Version",
        icon="mdi:cpu-64-bit",
        value_fn=lambda data: data.get("details", {}).get("invInfo", {}).get("fwversion") or "Unknown",
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="firmware_version",
        name="Firmware Version",
        icon="mdi:tag-outline",
        value_fn=lambda data: data.get("details", {}).get("invInfo", {}).get("fwName") or "Unknown",
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="total_work_time",
        name="Total Work Time",
        icon="mdi:timer-outline",
        value_fn=lambda data: data.get("details", {}).get("invInfo", {}).get("timeTotal2") or "Unknown",
        extra_attrs_fn=_get_work_time_attrs,
        is_basic=False,
    ),

    # ==========================================
    # 4. Battery Parameters & Telemetry
    # ==========================================
    AohaiSensorEntityDescription(
        key="battery_type",
        name="Battery Type",
        icon="mdi:battery-heart-variant",
        value_fn=_get_battery_type,
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="battery_priority",
        name="Battery Priority",
        icon="mdi:battery-charging-outline",
        value_fn=_get_battery_priority,
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="battery_status",
        name="Battery Status",
        icon="mdi:battery-sync",
        value_fn=_get_battery_status,
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="battery_voltage",
        name="Battery Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("vbat") or data.get("telemetry", {}).get("vbat", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="battery_current",
        name="Battery Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("bmSBatteryCurr") or data.get("telemetry", {}).get("bmSBatteryCurr", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="battery_max_charge_curr",
        name="Max Charge Current Allowed",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("bmSMaxChargeCurr", 0.0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="battery_max_discharge_curr",
        name="Max Discharge Current Allowed",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("bmSMaxDischargeCurr", 0.0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="battery_min_cell_voltage",
        name="Min Cell Voltage",
        native_unit_of_measurement="mV",
        icon="mdi:battery-minus",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("minCellVol", 0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="battery_max_cell_voltage",
        name="Max Cell Voltage",
        native_unit_of_measurement="mV",
        icon="mdi:battery-plus",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("maxCellVol", 0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="battery_temperature",
        name="Battery Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("bmSBatteryTemp", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="battery_rated_capacity",
        name="Battery Rated Capacity",
        native_unit_of_measurement="Ah",
        icon="mdi:battery-high",
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("bmSGaugeFCC", 0.0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="battery_charging_voltage",
        name="Battery Charging Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("bmSConstantVolt", 0.0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="battery_module_count",
        name="Battery Module Count",
        icon="mdi:view-grid",
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("moduleNum", 1),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="battery_cell_count",
        name="Battery Cell Count",
        icon="mdi:view-column",
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("cellNum", 16),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="battery_soc",
        name="Battery SOC",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("soC") if data.get("details", {}).get("invData", {}).get("soC") is not None else data.get("telemetry", {}).get("soc", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="battery_soh",
        name="Battery SOH",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:heart-pulse",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("bmSSOH", 100.0),
        is_basic=False,
    ),

    # ==========================================
    # 5. Real-Time Powers (Energy Dashboard & Flow) (BASIC)
    # ==========================================
    AohaiSensorEntityDescription(
        key="pv_total_power",
        name="PV Total Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("pvPower") or data.get("telemetry", {}).get("ppvAll", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="house_load_power",
        name="House Load Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("loadPower") or data.get("telemetry", {}).get("plocalLoadtotal", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="eps_output_power",
        name="EPS Backup Load Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("epsPower") or data.get("telemetry", {}).get("epSActPac1", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="battery_charging_power",
        name="Battery Charging Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("pcharge", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="battery_discharging_power",
        name="Battery Discharging Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("pdischarge", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="grid_active_power",
        name="Grid Active Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("pactogridtotal", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="extra_ac_power_to_grid",
        name="Grid Export Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("extraACPowertogrid", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="generator_active_power",
        name="Generator Active Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("genAcivePower", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="generator_phase_r_power",
        name="Generator Phase R Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("genAciveR", 0.0),
        is_basic=False,
    ),

    # ==========================================
    # 6. Voltages, Currents & Frequency
    # ==========================================
    AohaiSensorEntityDescription(
        key="pv1_voltage",
        name="PV1 Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("vpv1", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="pv1_power",
        name="PV1 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("ppv1", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="pv1_current",
        name="PV1 Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("calculated", {}).get("pv1_current", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="pv2_voltage",
        name="PV2 Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("vpv2", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="pv2_power",
        name="PV2 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("ppv2", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="pv2_current",
        name="PV2 Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("calculated", {}).get("pv2_current", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="ac_voltage_phase_r",
        name="Grid Voltage Phase R",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("vac1", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="grid_current",
        name="Grid Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("calculated", {}).get("grid_current", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="eps_current",
        name="EPS Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("calculated", {}).get("eps_current", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="eps_apparent_power",
        name="EPS Apparent Power",
        native_unit_of_measurement="VA",
        device_class=SensorDeviceClass.APPARENT_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("calculated", {}).get("eps_apparent_power", 0.0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="grid_frequency",
        name="Grid Frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("telemetry", {}).get("fac", 50.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="dc_bus_voltage",
        name="DC Bus Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("details", {}).get("invData", {}).get("dspBusTotalVolt", 0.0),
        is_basic=False,
    ),

    # ==========================================
    # 7. Energy Statistics (Home Assistant Energy Dashboard) (BASIC)
    # ==========================================
    AohaiSensorEntityDescription(
        key="daily_pv_energy",
        name="Daily PV Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("epVAllToday", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="total_pv_energy",
        name="Total PV Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("epvTotal", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="daily_load_energy",
        name="Daily Load Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("eloadToday", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="total_load_energy",
        name="Total Load Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("eloadTotal", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="daily_grid_in_energy",
        name="Daily Grid Energy Import",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("efromGridToday", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="total_grid_in_energy",
        name="Total Grid Energy Import",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("efromGridTotal", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="daily_grid_out_energy",
        name="Daily Grid Energy Export",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("etoGridToday", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="total_grid_out_energy",
        name="Total Grid Energy Export",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("etoGridTotal", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="daily_battery_charge_energy",
        name="Daily Battery Charge Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("echargeToday", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="daily_battery_discharge_energy",
        name="Daily Battery Discharge Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("edischargeToday", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="total_battery_charge_energy",
        name="Total Battery Charge Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("echargeTotal", 0.0),
        is_basic=True,
    ),
    AohaiSensorEntityDescription(
        key="total_battery_discharge_energy",
        name="Total Battery Discharge Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("edischargeTotal", 0.0),
        is_basic=True,
    ),

    # ==========================================
    # 8. Extended Energy & Self-Consumption Analytics
    # ==========================================
    AohaiSensorEntityDescription(
        key="self_consumption_today",
        name="Self-Consumption Today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("eselfToday", 0.0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="self_consumption_total",
        name="Self-Consumption Total",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("eselfTotal", 0.0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="input_energy_today",
        name="Total Energy Input Today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("inToday", 0.0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="input_energy_total",
        name="Total Energy Input Total",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("inTotal", 0.0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="solar_direct_to_load_today",
        name="Solar to Load Today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("deselfToLoadTodayEE", 0.0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="solar_direct_to_load_total",
        name="Solar to Load Total",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("deselfToLoadTotalEE", 0.0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="grid_direct_to_load_today",
        name="Grid to Load Today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("degridToLoadTodayEE", 0.0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="grid_direct_to_load_total",
        name="Grid to Load Total",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("degridToLoadTotalEE", 0.0),
        is_basic=False,
    ),

    # ==========================================
    # 9. Smart Battery Analytics & Moving Averages (AVG & ETA)
    # ==========================================
    AohaiSensorEntityDescription(
        key="battery_charge_eta",
        name="Battery Charge ETA",
        icon="mdi:battery-clock",
        value_fn=lambda data: data.get("calculated", {}).get("battery_charge_eta", "Standby"),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="battery_soc_speed",
        name="Battery SOC Speed",
        native_unit_of_measurement="%/h",
        icon="mdi:speedometer",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("calculated", {}).get("battery_soc_speed", 0.0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="battery_power_speed",
        name="Battery Power Speed",
        native_unit_of_measurement="W/h",
        icon="mdi:chart-line",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("calculated", {}).get("battery_power_speed", 0.0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="avg_pv_power",
        name="AVG PV Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("calculated", {}).get("avg_pv_power", 0.0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="avg_battery_power",
        name="AVG Battery Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("calculated", {}).get("avg_battery_power", 0.0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="avg_grid_power",
        name="AVG Grid Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("calculated", {}).get("avg_grid_power", 0.0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="avg_eps_load",
        name="AVG EPS Load",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("calculated", {}).get("avg_eps_load", 0.0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="avg_house_load",
        name="AVG House Load",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("calculated", {}).get("avg_house_load", 0.0),
        is_basic=False,
    ),

    # ==========================================
    # 10. Inverter Status & Advanced Settings Monitors
    # ==========================================
    AohaiSensorEntityDescription(
        key="max_inverter_power",
        name="Inverter Max Output Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        value_fn=lambda data: data.get("params", {}).get("maxInvPower", 6000.0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="afci_value",
        name="AFCI Detector Value",
        icon="mdi:shield-flash",
        value_fn=lambda data: data.get("params", {}).get("afCIValue2", 0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="ct_mode_status",
        name="CT Mode Status",
        icon="mdi:current-ac",
        value_fn=lambda data: "CT Enabled" if data.get("params", {}).get("ctMode") == 1 else "Meter / Disabled",
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="ct_ratio_status",
        name="CT Ratio Status",
        icon="mdi:numeric",
        value_fn=lambda data: data.get("params", {}).get("ctRatio", 0),
        is_basic=False,
    ),

    # ==========================================
    # 11. Environmental Savings & Diagnostics Log
    # ==========================================
    AohaiSensorEntityDescription(
        key="co2_reduction",
        name="CO2 Reduction Total",
        native_unit_of_measurement="kg",
        icon="mdi:molecule-co2",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("co2Total", 0.0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="tree_equivalent",
        name="Equivalent Trees Planted",
        icon="mdi:tree",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("telemetry", {}).get("treeTotal", 0.0),
        is_basic=False,
    ),
    AohaiSensorEntityDescription(
        key="last_telemetry_time",
        name="Last Telemetry Timestamp",
        icon="mdi:clock-check-outline",
        value_fn=lambda data: data.get("telemetry", {}).get("lastTime") or "Unknown",
        is_basic=True,
    ),
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up HaiPower sensors based on model profile."""
    coordinator: AohaiDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    cfg_profile = entry.options.get(CONF_ENTITY_MODE, entry.data.get(CONF_ENTITY_MODE, PROFILE_AUTO))
    effective_profile = get_effective_profile(cfg_profile, coordinator.model_name)

    if effective_profile == PROFILE_BASIC:
        descriptions = [d for d in SENSOR_TYPES if d.is_basic]
        _LOGGER.info("Setting up %d BASIC sensors for %s", len(descriptions), coordinator.dsn)
    elif effective_profile == PROFILE_AO_GSA_PRO:
        # Exclude CT clamp ratio status since AO-6KSL-G3 uses Smart Meter
        descriptions = [d for d in SENSOR_TYPES if d.key != "ct_ratio_status"]
        _LOGGER.info("Setting up %d sensors for %s (AO/GSA-PRO profile, Smart Meter)", len(descriptions), coordinator.dsn)
    else:
        descriptions = SENSOR_TYPES
        _LOGGER.info("Setting up %d sensors for %s (profile: %s)", len(descriptions), coordinator.dsn, effective_profile)

    entities = [AohaiSensor(coordinator, description) for description in descriptions]
    async_add_entities(entities)


class AohaiSensor(CoordinatorEntity[AohaiDataUpdateCoordinator], SensorEntity):
    """Representation of a HaiPower Inverter sensor."""

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

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return entity specific state attributes."""
        if self.coordinator.data is None:
            return None
        if self.entity_description.extra_attrs_fn:
            return self.entity_description.extra_attrs_fn(self.coordinator.data)
        return None
