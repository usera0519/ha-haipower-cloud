"""Constants for the HaiPower Cloud / Sandisolar integration."""

DOMAIN = "haipower_cloud"

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_DSN = "dsn"
CONF_CSN = "csn"
CONF_DEVICE_NAME = "device_name"
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 30

CONF_ENTITY_MODE = "entity_mode"

# Model Profiles / Functional Groups
PROFILE_AUTO = "auto"
PROFILE_AO_GSA_PRO = "ao_gsa_pro"
PROFILE_HSC_AH_1P = "hsc_ah_1p"
PROFILE_FSC_HSA_1P = "fsc_hsa_1p"
PROFILE_HUA_3P_LV = "hua_3p_lv"
PROFILE_HTA_3P_HV = "hta_3p_hv"
PROFILE_FSF_COMPACT = "fsf_compact"
PROFILE_FULL = "full"
PROFILE_BASIC = "basic"

ENTITY_MODE_FULL = PROFILE_FULL
ENTITY_MODE_BASIC = PROFILE_BASIC

MODEL_PROFILE_CHOICES = {
    PROFILE_AUTO: "Auto-Detect Model (Recommended)",
    PROFILE_AO_GSA_PRO: "AO-6KSL-G3 / GSA-PRO Series (1P 48V LV, Smart Meter, Smart Load, Gen)",
    PROFILE_HSC_AH_1P: "HSC / AH / FSA Series (1P 48V LV, Dual MPPT, CT Clamp & Meter, EPS)",
    PROFILE_FSC_HSA_1P: "FSC / HSA Series (1P 48V LV 8-12kW High Power)",
    PROFILE_HUA_3P_LV: "HUA Series (3-Phase 400V, 48V LV Battery)",
    PROFILE_HTA_3P_HV: "HTA / AH-TH Series (3-Phase 400V, High-Voltage 150-800V Battery)",
    PROFILE_FSF_COMPACT: "FSF Series (1-Phase 230V, 12V/24V Compact Balcony/RV)",
    PROFILE_FULL: "Full Mode (Expose all entities without model filtering)",
    PROFILE_BASIC: "Basic Mode (Essential Energy Dashboard + Inverter On/Off)",
}

def get_effective_profile(configured_profile: str, model_str: str) -> str:
    """Resolve effective functional group given configured choice and detected hardware string."""
    if configured_profile not in (PROFILE_AUTO, None, ""):
        return configured_profile

    # Auto-detection from hardware string (e.g. 'AO-6KSL-G3', 'SD-PRO-EU 6.5K', 'HSC-6K1P-BL')
    m = (model_str or "").upper()
    # Check Three-Phase High-Voltage first (HTA, KTH, KTHD, BH)
    if any(k in m for k in ["HTA-", "KTH", "KTHD", "BH"]):
        return PROFILE_HTA_3P_HV
    elif any(k in m for k in ["HUA-"]):
        return PROFILE_HUA_3P_LV
    elif any(k in m for k in ["FSC-", "HSA-"]):
        return PROFILE_FSC_HSA_1P
    elif any(k in m for k in ["HSC-", "AH-", "FSA-"]):
        return PROFILE_HSC_AH_1P
    elif any(k in m for k in ["FSF-"]):
        return PROFILE_FSF_COMPACT
    elif any(k in m for k in ["AO-", "GSA-", "SD-PRO", "SD-HYM"]):
        return PROFILE_AO_GSA_PRO

    # Default fallback for Sandisolar / HaiPower
    return PROFILE_AO_GSA_PRO


# Power Supply Priority: SOL (Solar/PV Priority), UTI (Utility Priority), SBU (Solar-Battery-Utility Priority)
POWER_PRIORITY_OPTIONS = [
    "SOL (Solar/PV Priority)",
    "UTI (Utility Priority)",
    "SBU (Solar-Battery-Utility Priority)",
]
POWER_PRIORITY_TO_VAL = {
    "SOL (Solar/PV Priority)": 0,
    "UTI (Utility Priority)": 1,
    "SBU (Solar-Battery-Utility Priority)": 2,
}
VAL_TO_POWER_PRIORITY = {
    0: "SOL (Solar/PV Priority)",
    1: "UTI (Utility Priority)",
    2: "SBU (Solar-Battery-Utility Priority)",
}

# Battery Charging Priority: CSO (Solar Priority), SNU (Solar + Utility Hybrid), OSO (Only Solar)
CHARGING_PRIORITY_OPTIONS = [
    "CSO (Solar Priority)",
    "SNU (Solar + Utility Hybrid)",
    "OSO (Only Solar)",
]
CHARGING_PRIORITY_TO_VAL = {
    "CSO (Solar Priority)": 0,
    "SNU (Solar + Utility Hybrid)": 1,
    "OSO (Only Solar)": 2,
}
VAL_TO_CHARGING_PRIORITY = {
    0: "CSO (Solar Priority)",
    1: "SNU (Solar + Utility Hybrid)",
    2: "OSO (Only Solar)",
}

# Grid Input Voltage Range (APL: 90~280V wide, UPS: 170~280V narrow)
AC_INPUT_MODE_OPTIONS = [
    "APL (Appliance - Wide 90-280V)",
    "UPS (UPS - Narrow 170-280V)",
]
AC_INPUT_MODE_TO_VAL = {
    "APL (Appliance - Wide 90-280V)": 0,
    "UPS (UPS - Narrow 170-280V)": 1,
}
VAL_TO_AC_INPUT_MODE = {
    0: "APL (Appliance - Wide 90-280V)",
    1: "UPS (UPS - Narrow 170-280V)",
}

AC_INPUT_OPTIONS = AC_INPUT_MODE_OPTIONS
AC_INPUT_TO_VAL = AC_INPUT_MODE_TO_VAL
VAL_TO_AC_INPUT = VAL_TO_AC_INPUT_MODE

# GEN Port Work Mode
GEN_MODE_OPTIONS = [
    "Generator",
    "Microinverter / AC Input",
    "Smart Load Output",
]
GEN_MODE_TO_VAL = {
    "Generator": 0,
    "Microinverter / AC Input": 1,
    "Smart Load Output": 2,
}
VAL_TO_GEN_MODE = {
    0: "Generator",
    1: "Microinverter / AC Input",
    2: "Smart Load Output",
}

# Inverter Fault Codes mapping (Section 7.1 in manual)
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

# Inverter Warning / Alarm Codes mapping (Section 7.1 in manual)
WARN_CODE_MAP = {
    0: "Normal (No Warning)",
    103: "Grid unavailable",
    104: "Grid voltage out of range",
    105: "Grid frequency out of range",
    106: "No output voltage from generator",
    107: "Generator output voltage out of range",
    108: "Generator output frequency out of range",
    302: "Low battery",
    304: "Abnormal BMS data",
    305: "Low battery voltage alarm",
    502: "Abnormal memory read/write",
}

# Battery Type mapping
BATTERY_TYPE_MAP = {
    0: "Lead-Acid Battery",
    1: "Lithium Battery with BMS",
    2: "Li-Ion Battery (No Communication)",
}

# Battery Priority mapping
BATTERY_PRIORITY_MAP = {
    0: "Load Priority",
    1: "Battery Priority",
    2: "Grid Priority",
    3: "Power Selling Mode",
    4: "Load Side Self-Consumption",
    5: "CT Side Self-Consumption",
    6: "Load Side Surplus Online",
    7: "CT Side Surplus Online",
}

# Running / Operation Mode mapping
OPERATION_MODE_MAP = {
    0: "PV Priority Mode (SOL)",
    1: "Mains Priority Mode (UTI)",
    2: "Inverter Priority Mode (SBU)",
    10: "Grid Output Mode",
}
