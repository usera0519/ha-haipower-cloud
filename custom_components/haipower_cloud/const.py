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
ENTITY_MODE_FULL = "full"
ENTITY_MODE_BASIC = "basic"
ENTITY_MODES = [ENTITY_MODE_FULL, ENTITY_MODE_BASIC]

# Power Supply Priority: SOL (PV Priority), UTI (Mains/Grid Priority), SBU (Solar-Battery-Utility)
POWER_PRIORITY_OPTIONS = [
    "SOL (Solar/PV First - Najpierw Fotowoltaika)",
    "UTI (Utility/Grid First - Najpierw Sieć AC)",
    "SBU (Solar-Battery-Utility - Fotowoltaika -> Bateria -> Sieć)",
]
POWER_PRIORITY_TO_VAL = {
    "SOL (Solar/PV First - Najpierw Fotowoltaika)": 0,
    "UTI (Utility/Grid First - Najpierw Sieć AC)": 1,
    "SBU (Solar-Battery-Utility - Fotowoltaika -> Bateria -> Sieć)": 2,
}
VAL_TO_POWER_PRIORITY = {
    0: "SOL (Solar/PV First - Najpierw Fotowoltaika)",
    1: "UTI (Utility/Grid First - Najpierw Sieć AC)",
    2: "SBU (Solar-Battery-Utility - Fotowoltaika -> Bateria -> Sieć)",
}

# Battery Charging Priority: CSO (PV Priority), SNU (Hybrid PV+Grid), OSO (Solar Only)
CHARGING_PRIORITY_OPTIONS = [
    "CSO (Solar First - Ładowanie głównie z PV)",
    "SNU (Solar + Grid - Ładowanie z PV i Sieci jednocześnie)",
    "OSO (Only Solar - Ładowanie wyłącznie z PV)",
]
CHARGING_PRIORITY_TO_VAL = {
    "CSO (Solar First - Ładowanie głównie z PV)": 0,
    "SNU (Solar + Grid - Ładowanie z PV i Sieci jednocześnie)": 1,
    "OSO (Only Solar - Ładowanie wyłącznie z PV)": 2,
}
VAL_TO_CHARGING_PRIORITY = {
    0: "CSO (Solar First - Ładowanie głównie z PV)",
    1: "SNU (Solar + Grid - Ładowanie z PV i Sieci jednocześnie)",
    2: "OSO (Only Solar - Ładowanie wyłącznie z PV)",
}

# Grid Input Voltage Range (APL: 90~280V wide, UPS: 170~280V narrow)
AC_INPUT_MODE_OPTIONS = [
    "APL (Appliance - Szeroki zakres napięcia sieci 90-280V)",
    "UPS (UPS - Wąski zakres napięcia sieci 170-280V)",
]
AC_INPUT_MODE_TO_VAL = {
    "APL (Appliance - Szeroki zakres napięcia sieci 90-280V)": 0,
    "UPS (UPS - Wąski zakres napięcia sieci 170-280V)": 1,
}
VAL_TO_AC_INPUT_MODE = {
    0: "APL (Appliance - Szeroki zakres napięcia sieci 90-280V)",
    1: "UPS (UPS - Wąski zakres napięcia sieci 170-280V)",
}

AC_INPUT_OPTIONS = AC_INPUT_MODE_OPTIONS
AC_INPUT_TO_VAL = AC_INPUT_MODE_TO_VAL
VAL_TO_AC_INPUT = VAL_TO_AC_INPUT_MODE

# GEN Port Work Mode (Tryb pracy portu generatora)
GEN_MODE_OPTIONS = [
    "Generator (Agregat prądotwórczy)",
    "Microinverter / Inverter input (Mikrofalownik / Wejście zasilania)",
    "Smart Load output (Zasilanie odbiorników niekrytycznych)",
]
GEN_MODE_TO_VAL = {
    "Generator (Agregat prądotwórczy)": 0,
    "Microinverter / Inverter input (Mikrofalownik / Wejście zasilania)": 1,
    "Smart Load output (Zasilanie odbiorników niekrytycznych)": 2,
}
VAL_TO_GEN_MODE = {
    0: "Generator (Agregat prądotwórczy)",
    1: "Microinverter / Inverter input (Mikrofalownik / Wejście zasilania)",
    2: "Smart Load output (Zasilanie odbiorników niekrytycznych)",
}

# Inverter Fault Codes mapping (from Section 7.1 in manual)
FAULT_CODE_MAP = {
    0: "Brak błędów (Normal)",
    103: "Inverter DC offset too high",
    105: "Bypass AC output overloaded (Przeciążenie wyjścia Bypass)",
    200: "Off-grid output voltage too low (Zbyt niskie napięcie off-grid)",
    201: "Off-grid output voltage too high (Zbyt wysokie napięcie off-grid)",
    202: "Off-grid output short circuit (Zwarcie wyjścia off-grid)",
    203: "Off-grid output overloaded (Przeciążenie wyjścia off-grid)",
    204: "Abnormal off-grid DC component offset",
    301: "Battery open circuit (Rozwarcie obwodu baterii)",
    305: "Battery overvoltage (Zbyt wysokie napięcie baterii)",
    306: "Battery overcurrent (Zbyt wysoki prąd baterii)",
    307: "Battery communication fault (Błąd komunikacji z baterią BMS)",
    308: "BMS fault (Błąd BMS)",
    400: "PV overvoltage (Zbyt wysokie napięcie paneli PV)",
    403: "PV short circuit (Zwarcie paneli PV)",
    404: "PV reverse connection (Odwrotna polaryzacja paneli PV)",
    500: "Abnormal BUS voltage (Nieprawidłowe napięcie szyny DC)",
    501: "Abnormal BUS voltage sampling",
    502: "Abnormal internal device communication (Błąd komunikacji wewnętrznej)",
    505: "Abnormal temperature sensor connection (Błąd czujnika temperatury)",
    506: "Device over-temperature (Przegrzanie urządzenia)",
    507: "Abnormal relay (Błąd przekaźnika)",
    509: "Anti-counter-current output timeout",
    510: "Mismatched software version",
    511: "Fan fault (Błąd wentylatora)",
    513: "Parallel abnormality (Błąd pracy równoległej)",
}

# Inverter Warning / Alarm Codes mapping (from Section 7.1 in manual)
WARN_CODE_MAP = {
    0: "Brak ostrzeżeń (Normal)",
    103: "Grid unavailable (Brak sieci zasilającej AC)",
    104: "Overrange voltage of grid (Napięcie sieci poza zakresem)",
    105: "Overrange frequency of grid (Częstotliwość sieci poza zakresem)",
    106: "No output voltage from generator (Brak napięcia z agregatu)",
    107: "Overrange output voltage of generator",
    108: "Overrange output frequency of generator",
    302: "Low battery (Niski poziom naładowania baterii)",
    304: "Abnormal BMS information (Błąd danych z BMS)",
    305: "Low battery voltage alarm (Alarm niskiego napięcia baterii)",
    502: "Abnormal memory reading and writing",
}

# Battery Type mapping
BATTERY_TYPE_MAP = {
    0: "Lead-acid Battery (Kwasowo-ołowiowa)",
    1: "Lithium Battery with BMS (Litowa z komunikacją BMS)",
    2: "Li-ion Battery No Comm (Litowa bez komunikacji)",
}

# Battery Priority mapping
BATTERY_PRIORITY_MAP = {
    0: "Load Priority (Zasilanie odbiorników w pierwszej kolejności)",
    1: "Battery Priority (Ładowanie baterii w pierwszej kolejności)",
    2: "Grid Priority (Sprzedaż/oddawanie do sieci)",
    3: "Power Selling Mode (Tryb sprzedaży energii)",
    4: "Load Side Self Gen & Self Use (Autokonsumpcja odbiorników)",
    5: "CT Side Self Gen & Self Use (Autokonsumpcja z przekładnikiem CT)",
    6: "Load Side Surplus Power Online (Nadwyżka z odbiorników do sieci)",
    7: "CT Side Surplus Power Online (Nadwyżka z CT do sieci)",
}

# Running / Operation Mode mapping
OPERATION_MODE_MAP = {
    0: "PV Priority Mode / Tryb SOL (Fotowoltaika)",
    1: "Mains Priority Mode / Tryb UTI (Sieć AC)",
    2: "Inverter Priority Mode / Tryb SBU (Falownik/Bateria)",
    10: "Grid Output Mode / Tryb pracy sieciowej",
}
