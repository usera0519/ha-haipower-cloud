"""Constants for the HaiPower Cloud / Sandisolar integration."""

DOMAIN = "haipower_cloud"

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_DSN = "dsn"
CONF_CSN = "csn"
CONF_DEVICE_NAME = "device_name"
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 30

# System Operating Mode Settings (Section 4.9.1 in manual)
# Power Supply Priority: SOL (PV Priority), UTI (Mains Priority), SBU (Inverter Priority)
POWER_PRIORITY_OPTIONS = [
    "SOL (PV Priority)",
    "UTI (Mains Priority)",
    "SBU (Inverter Priority)",
]
POWER_PRIORITY_TO_VAL = {
    "SOL (PV Priority)": 0,
    "UTI (Mains Priority)": 1,
    "SBU (Inverter Priority)": 2,
}
VAL_TO_POWER_PRIORITY = {
    0: "SOL (PV Priority)",
    1: "UTI (Mains Priority)",
    2: "SBU (Inverter Priority)",
}

# Battery Charging Priority: CSO (PV Priority), SNU (Hybrid Charging), OSO (PV Only Charging)
# Note: In the printed manual this was typoed as OSS, but in inverter firmware and settings it is OSO (Only Solar).
CHARGING_PRIORITY_OPTIONS = [
    "CSO (PV Priority)",
    "SNU (Hybrid Charging)",
    "OSO (PV Only Charging)",
]
CHARGING_PRIORITY_TO_VAL = {
    "CSO (PV Priority)": 0,
    "SNU (Hybrid Charging)": 1,
    "OSO (PV Only Charging)": 2,
}
VAL_TO_CHARGING_PRIORITY = {
    0: "CSO (PV Priority)",
    1: "SNU (Hybrid Charging)",
    2: "OSO (PV Only Charging)",
}

# Grid Input Voltage Range (Section 4.9.4 in manual)
# APL: 90~280VAC (Wide range)
# UPS: 170~265VAC (Narrow range)
AC_INPUT_MODE_OPTIONS = [
    "APL (Wide 90-280V)",
    "UPS (Narrow 170-265V)",
]
AC_INPUT_MODE_TO_VAL = {
    "APL (Wide 90-280V)": 0,
    "UPS (Narrow 170-265V)": 1,
}
VAL_TO_AC_INPUT_MODE = {
    0: "APL (Wide 90-280V)",
    1: "UPS (Narrow 170-265V)",
}

AC_INPUT_OPTIONS = AC_INPUT_MODE_OPTIONS
AC_INPUT_TO_VAL = AC_INPUT_MODE_TO_VAL
VAL_TO_AC_INPUT = VAL_TO_AC_INPUT_MODE

# Inverter Fault Codes mapping (from Section 7.1 in manual)
FAULT_CODE_MAP = {
    0: "Normal (No Fault)",
    103: "Inverter DC offset too high",
    105: "Bypass AC output overloaded",
    200: "Off-grid output voltage too low",
    201: "Off-grid output voltage too high",
    202: "Off-grid output short circuit",
    203: "Off-grid output overloaded",
    204: "Abnormal off-grid DC component offset",
    301: "Battery open circuit",
    305: "Battery overvoltage",
    306: "Battery overcurrent",
    307: "Battery communication fault",
    308: "BMS fault",
    400: "PV overvoltage",
    403: "PV short circuit",
    404: "PV reverse connection",
    500: "Abnormal BUS voltage",
    501: "Abnormal BUS voltage sampling",
    502: "Abnormal internal device communication",
    505: "Abnormal temperature sensor connection",
    506: "Device over-temperature",
    507: "Abnormal relay",
    509: "Anti-counter-current output timeout",
    510: "Mismatched software version",
    511: "Fan fault",
    513: "Parallel abnormality",
}

# Inverter Warning / Alarm Codes mapping (from Section 7.1 in manual)
WARN_CODE_MAP = {
    0: "Normal (No Warning)",
    103: "Grid unavailable",
    104: "Overrange voltage of grid",
    105: "Overrange frequency of grid",
    106: "No output voltage from generator",
    107: "Overrange output voltage of generator",
    108: "Overrange output frequency of generator",
    302: "Low battery",
    304: "Abnormal BMS information",
    305: "Low battery voltage alarm",
    502: "Abnormal memory reading and writing",
}

# Battery Type mapping
BATTERY_TYPE_MAP = {
    0: "Lead-acid Battery",
    1: "Lithium Battery",
    2: "Li-ion Battery (No Comm)",
}

# Battery Priority mapping
BATTERY_PRIORITY_MAP = {
    0: "Load Priority",
    1: "Battery Priority",
    2: "Grid Priority",
    3: "Power Selling Mode",
    4: "Load Side Self Gen & Self Use",
    5: "CT Side Self Gen & Self Use",
    6: "Load Side Surplus Power Online",
    7: "CT Side Surplus Power Online",
}

# Running / Operation Mode mapping
OPERATION_MODE_MAP = {
    0: "PV Priority Mode (SOL)",
    1: "Mains Priority Mode (UTI)",
    2: "Inverter Priority Mode (SBU)",
    10: "Grid Output Mode",
}
