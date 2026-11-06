# HaiPower Cloud / Sandisolar - Comprehensive Entities Catalog & Model Compatibility

This document provides a complete technical explanation for all entities exposed by the `haipower_cloud` Home Assistant integration, based on the engineering manuals for **Aohai Digital Power**, **Sandisolar**, and OEM partner inverters.

---

## 1. Supported Inverter Families & Architectural Groups

Based on the 18 official technical manuals located in the `manuals/` directory, all supported inverters have been categorized into **6 functional groups** sharing hardware capabilities, wiring interfaces, and register sets:

### Group 1: `AO / GSA-PRO` Family (Residential 1-Phase 48V LV - Smart Meter, Smart Load & Generator)
* **Covered Inverter Models (from manuals):**
  * **AO-3~6KSL-G1:** AO-3KSL-G1, AO-4KSL-G1, AO-5KSL-G1, AO-6KSL-G1
  * **AO-3~4KSL-G2 & AO-5~6KSL-G2:** AO-3KSL-G2, AO-4KSL-G2, AO-5KSL-G2, AO-6KSL-G2
  * **AO-3~6KSL-G3:** AO-3KSL-G3, AO-4KSL-G3, AO-5KSL-G3, **AO-6KSL-G3** *(Primary verified model)*
  * **GSA-5~6.2K1P-BL & GSA-5~6.2K1P-BL-PRO:** GSA-5K1P-BL, GSA-6.2K1P-BL, GSA-5K1P-BL-PRO, GSA-6.2K1P-BL-PRO
  * **SD-PRO-EU Series:** SD-PRO-EU 6.5K (OEM Sandisolar)
  * **SD-HYM Series:** SD-HYM-4862HWP (IP65 Outdoor Hybrid)
* **Electrical Architecture:** Single-phase 230V AC, 48V Low-Voltage battery (40V–60V DC), single high-current MPPT (up to 40A DC, 90–450V DC operating range, max Voc 500V DC).
* **Metering & Anti-Backflow:** **RS485 Smart Meter** (connected to RJ45 pins 7 & 8; register 88 `ctMode`: `0 = Smart Meter`, `1 = CT`). **Notice:** The physical `AO-6KSL-G3` inverter has **no physical CT clamp port** on its terminal panel. Zero-export anti-backflow is performed via the RS485 Smart Meter. Consequently, CT clamp calibration/detection buttons and CT current ratio settings are automatically excluded in this profile to prevent confusion.
* **AC Outputs & Generator:** Dual AC outputs (Main UPS output + Smart Load secondary output with separate cutoff voltage/SOC thresholds), Generator dry contact auto-start, parallel operation up to 6 units.

---

### Group 2: `HSC / AH 1P` Family (Residential 1-Phase 48V LV - Dual MPPT, CT Clamp & Meter, EPS)
* **Covered Inverter Models (from manuals):**
  * **HSC-3~8K1P-BL:** HSC-3K1P-BL, HSC-3.6K1P-BL, HSC-4K1P-BL, HSC-5K1P-BL, HSC-6K1P-BL, HSC-8K1P-BL
  * **AH-3~6KSL-G2:** AH-3KSL-G2, AH-3.6KSL-G2, AH-4KSL-G2, AH-4.6KSL-G2, AH-5KSL-G2, AH-6KSL-G2
  * **FSA-3~4K1P-BL:** FSA-3K1P-BL, FSA-4K1P-BL
* **Electrical Architecture:** Single-phase 230V AC, 48V Low-Voltage battery (40V–60V DC), **dual independent MPPT trackers** (ideal for East-West roof orientations).
* **Metering & Anti-Backflow:** Supports both **physical external CT clamp** (with calibration command `reg 96=1` and direction detection `reg 96=2`) and RS485 energy meters.
* **Special Capabilities:** <10ms UPS switchover, peak shaving, Time-of-Use (TOU) scheduled tariffs, microinverter AC coupling on the GEN port.

---

### Group 3: `FSC / HSA 1P` Family (High-Power Residential 1-Phase 48V LV - 8kW to 12kW)
* **Covered Inverter Models (from manuals):**
  * **FSC-8~12K1P-BL & FSC-8~12K1P-BL-G3:** FSC-8K1P-BL, FSC-10K1P-BL, FSC-12K1P-BL, FSC-8K1P-BL-G3, FSC-10K1P-BL-G3, FSC-12K1P-BL-G3
  * **HSA-8~12K1P-BL:** HSA-8K1P-BL, HSA-10K1P-BL, HSA-12K1P-BL
* **Electrical Architecture:** Single-phase 230V AC, 48V Low-Voltage battery with high battery current capability (up to 220A charge/discharge).
* **Metering & Anti-Backflow:** Physical CT clamp inputs and RS485 smart meters, full CT calibration and detection support.
* **Special Capabilities:** 3 to 4 MPPT strings, parallel operation up to 16 units, heavy generator auto-start with programmable power limits.

---

### Group 4: `HUA 3P LV` Family (Commercial/Residential 3-Phase 400V - 48V Low-Voltage Battery)
* **Covered Inverter Models (from manuals):**
  * **HUA-8~15K3P-BL:** HUA-8K3P-BL, HUA-10K3P-BL, HUA-12K3P-BL, HUA-15K3P-BL
* **Electrical Architecture:** Three-phase 400V AC (3L + N + PE), **48V Low-Voltage battery** (40V–60V DC, standard 48V server rack / LiFePO4 batteries).
* **Key Features:** **100% unbalanced three-phase output** (each phase can deliver up to 50% of total rated power independently), dual MPPTs, 3-phase Smart Meter (Acrel/Chint) or 3-phase CT clamps, dual EPS backup circuits.

---

### Group 5: `HTA / AH-TH 3P HV` Family (Commercial 3-Phase 400V - High-Voltage 150V–800V Battery)
* **Covered Inverter Models (from manuals):**
  * **HTA-15~30K3P-BH:** HTA-15K3P-BH, HTA-20K3P-BH, HTA-25K3P-BH, HTA-30K3P-BH
  * **AH-4~10KTH-G1:** AH-4KTH-G1, AH-5KTH-G1, AH-6KTH-G1, AH-8KTH-G1, AH-10KTH-G1
  * **AHW-6~10KTHD-G1:** AHW-6KTHD-G1, AHW-8KTHD-G1, AHW-10KTHD-G1
* **Electrical Architecture:** Three-phase 400V AC (3L + N + PE), **High-Voltage Battery System (150V–800V DC)**.
* **PV Inputs:** 2 to 4 high-voltage MPPT trackers (up to 1000V DC Voc, max 45kW PV power).
* **Notice:** Low-voltage battery thresholds (e.g. 48V–58V float/CV voltage, 42V low cutoff) do not apply to this family; the high-voltage BMS communicates pack parameters directly over CAN bus.

---

### Group 6: `FSF Compact` Family (1-Phase 230V - 12V/24V Compact Balcony / RV Storage)
* **Covered Inverter Models (from manuals):**
  * **FSF-1.5~2K1P-BL:** FSF-1.5K1P-BL, FSF-2K1P-BL
* **Electrical Architecture:** Single-phase 230V AC, 12V or 24V Low-Voltage battery.
* **Design Purpose:** Balcony solar systems, off-grid cabins, mobile RV / camper installations.
* **Notice:** Single MPPT (30–400V), single AC output. No generator dry contact, no smart load secondary output, no external CT clamp.

---

## 2. Inverter Model Compatibility Matrix

> **Legend:**
> * `✓` = Fully supported and verified by hardware specification and cloud register mapping.
> * `❌` = Not supported by this inverter hardware architecture (e.g. physical CT clamp on AO-6KSL-G3, 48V thresholds on High-Voltage inverters, generator controls on FSF).
> * `?` = Optional feature, depends on installed accessory card (e.g. AFCI arc-fault module) or firmware release.

| Entity Name | Key | Type | Group 1: AO / GSA-PRO | Group 2: HSC / AH 1P | Group 3: FSC / HSA 1P | Group 4: HUA 3P LV | Group 5: HTA 3P HV | Group 6: FSF Compact | Full Profile | Basic Profile |
|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Inverter Operation** | `power_switch` | Switch | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Audible Buzzer** | `buzzer_switch` | Switch | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ |
| **Anti-Backflow (Zero Export)** | `anti_backflow_switch` | Switch | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ | ✓ | ❌ |
| **External CT / Meter Enable** | `ct_enable` | Switch | ✓ (Meter) | ✓ (CT/Meter) | ✓ (CT/Meter) | ✓ | ✓ | ❌ | ✓ | ❌ |
| **Overload to Bypass** | `overload_to_bypass` | Switch | ✓ | ✓ | ✓ | ✓ | ? | ✓ | ✓ | ❌ |
| **Zero Power Output** | `zero_current_enable` | Switch | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ | ✓ | ❌ |
| **VFRT Enable** | `vfrt_enable` | Switch | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ | ✓ | ❌ |
| **Generator Dry Contact** | `generator_dry_contact` | Switch | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ | ✓ | ❌ |
| **AC Grid Charging** | `ac_charge_enable_switch` | Switch | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ |
| **EPS Output** | `eps_enable_switch` | Switch | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ |
| **Bypass Mode** | `bypass_enable_switch` | Switch | ✓ | ✓ | ✓ | ✓ | ? | ✓ | ✓ | ❌ |
| **Generator Charging** | `gen_charge_enable_switch` | Switch | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ | ✓ | ❌ |
| **Battery Equalization** | `equalization_switch` | Switch | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ |
| **Force Full Charge** | `force_full_charge_switch` | Switch | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ |
| **Bluetooth Broadcast** | `bluetooth_switch` | Switch | ✓ | ? | ? | ? | ? | ? | ✓ | ❌ |
| **Force Inverter Data Refresh** | `refresh_button` | Button | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ |
| **CT Calibration** | `ct_calibration` | Button | ❌ *(Meter)* | ✓ | ✓ | ? | ❌ *(Meter)* | ❌ | ✓ | ❌ |
| **CT Detection** | `ct_detection` | Button | ❌ *(Meter)* | ✓ | ✓ | ? | ❌ *(Meter)* | ❌ | ✓ | ❌ |
| **Power Supply Priority** | `power_priority` | Select | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ |
| **Charging Priority** | `charging_priority` | Select | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ |
| **Grid Input Voltage Range** | `ac_input_type` | Select | ✓ | ✓ | ✓ | ✓ | ? | ✓ | ✓ | ❌ |
| **GEN Port Work Mode** | `gen_port_mode` | Select | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ | ✓ | ❌ |
| **Max Battery Charge Current** | `max_battery_charge_current` | Number | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ |
| **AC Grid Charge Current** | `ac_charging_current_limit` | Number | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ |
| **Generator Charge Current** | `generator_charging_current_limit`| Number | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ | ✓ | ❌ |
| **Generator Rated Power** | `generator_input_power` | Number | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ | ✓ | ❌ |
| **CT Current Ratio (1~3000)** | `ct_current_ratio` | Number | ❌ *(Meter)* | ✓ | ✓ | ? | ❌ *(Meter)* | ❌ | ✓ | ❌ |
| **Battery Charging CV Voltage** | `vbat_constant_charge` | Number | ✓ | ✓ | ✓ | ✓ | ❌ *(HV)* | ✓ (12V scaled) | ✓ | ❌ |
| **Battery Float Voltage** | `vbat_floating_charge` | Number | ✓ | ✓ | ✓ | ✓ | ❌ *(HV)* | ✓ (12V scaled) | ✓ | ❌ |
| **Battery to Grid Voltage (SBU)** | `bat2ac_volt` | Number | ✓ | ✓ | ✓ | ✓ | ❌ *(HV)* | ✓ (12V scaled) | ✓ | ❌ |
| **Grid to Battery Voltage (SBU)** | `ac2bat_volt` | Number | ✓ | ✓ | ✓ | ✓ | ❌ *(HV)* | ✓ (12V scaled) | ✓ | ❌ |
| **Battery Low-Voltage Cutoff** | `vbat_stop_discharge` | Number | ✓ | ✓ | ✓ | ✓ | ❌ *(HV)* | ✓ (12V scaled) | ✓ | ❌ |
| **Battery Under-Voltage Alarm** | `bat_undervolt_alarm` | Number | ✓ | ✓ | ✓ | ✓ | ❌ *(HV)* | ✓ (12V scaled) | ✓ | ❌ |
| **Low-Voltage Recovery** | `bat_lv_restart_volt` | Number | ✓ | ✓ | ✓ | ✓ | ❌ *(HV)* | ✓ (12V scaled) | ✓ | ❌ |
| **Battery Recharge Threshold** | `bat_need_charge_volt` | Number | ✓ | ✓ | ✓ | ✓ | ❌ *(HV)* | ✓ (12V scaled) | ✓ | ❌ |
| **Over-Voltage Disconnect** | `bat_overvolt_disconnect` | Number | ✓ | ✓ | ✓ | ✓ | ❌ *(HV)* | ✓ (12V scaled) | ✓ | ❌ |
| **On-Grid Discharge Cutoff SOC** | `grid_first_stop_soc` | Number | ✓ | ✓ | ✓ | ✓ | ✓ | ? | ✓ | ❌ |
| **On-Grid Recovery SOC** | `grid_recover_soc` | Number | ✓ | ✓ | ✓ | ✓ | ✓ | ? | ✓ | ❌ |
| **Off-Grid Discharge Cutoff SOC**| `offline_stop_soc` | Number | ✓ | ✓ | ✓ | ✓ | ✓ | ? | ✓ | ❌ |
| **Off-Grid Recovery SOC** | `offline_recover_soc` | Number | ✓ | ✓ | ✓ | ✓ | ✓ | ? | ✓ | ❌ |
| **Charging Cutoff SOC** | `charging_cutoff_soc` | Number | ✓ | ✓ | ✓ | ✓ | ✓ | ? | ✓ | ❌ |
| **Smart Load Cutoff SOC** | `smart_load_cutoff_soc` | Number | ✓ | ? | ✓ | ? | ✓ | ❌ | ✓ | ❌ |
| **Smart Load Cutoff Voltage** | `smart_load_cutoff_volt` | Number | ✓ | ? | ✓ | ? | ❌ *(HV)* | ❌ | ✓ | ❌ |
| **Smart Load Recovery SOC** | `smart_load_recover_soc` | Number | ✓ | ? | ✓ | ? | ✓ | ❌ | ✓ | ❌ |
| **Smart Load Recovery Voltage** | `smart_load_recover_volt` | Number | ✓ | ? | ✓ | ? | ❌ *(HV)* | ❌ | ✓ | ❌ |
| **Anti-Reverse Grid Compensation**| `grid_power_compensation`| Number | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ | ✓ | ❌ |
| **Active Power Rate Limit** | `active_power_rate` | Number | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ |
| **PV Total Power** | `pv_total_power` | Sensor | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **House Load Power** | `house_load_power` | Sensor | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **EPS Backup Load Power** | `eps_output_power` | Sensor | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Battery Charging Power** | `battery_charging_power` | Sensor | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Battery Discharging Power** | `battery_discharging_power`| Sensor | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Grid Active Power** | `grid_active_power` | Sensor | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Grid Export Power** | `extra_ac_power_to_grid` | Sensor | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ | ✓ | ✓ |
| **Generator Active Power** | `generator_active_power` | Sensor | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ | ✓ | ✓ |
| **Battery Voltage & Current** | `battery_voltage`/`current` | Sensor | ✓ | ✓ | ✓ | ✓ | ✓ (HV) | ✓ | ✓ | ✓ |
| **Battery SOC & Temperature** | `battery_soc`/`temp` | Sensor | ✓ | ✓ | ✓ | ✓ | ✓ | ? | ✓ | ✓ |
| **PV1 Voltage & Current** | `pv1_voltage`/`current` | Sensor | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **PV2 Voltage & Current** | `pv2_voltage`/`current` | Sensor | ? (Dual string) | ✓ | ✓ | ✓ | ✓ | ❌ | ✓ | ✓ |
| **Grid Frequency & Voltage** | `grid_frequency`/`voltage`| Sensor | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Energy Dashboard Statistics** | `daily_pv_energy`, etc. | Sensor | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Moving Averages (AVG 5m)** | `avg_pv_power`, etc. | Sensor | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ |
| **Battery ETA & Speed** | `battery_charge_eta`, etc. | Sensor | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ |
| **AFCI Arc Detector Value** | `afci_value` | Sensor | ? (with AFCI) | ? | ? | ? | ✓ | ❌ | ✓ | ❌ |
| **CT Mode Status** | `ct_mode_status` | Sensor | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ | ✓ | ❌ |
| **CT Ratio Status** | `ct_ratio_status` | Sensor | ❌ *(Meter)* | ✓ | ✓ | ? | ❌ *(Meter)* | ❌ | ✓ | ❌ |

---

## 3. Detailed Entity Encyclopedia

### 3.1 Switches Platform

#### `Inverter Operation` (`power_switch`)
* **Cloud Parameter:** `onOff` / `inveterOnOff` / `telemetry.onoff`
* **Description:** Master software power switch for the inverter. When toggled OFF, the inverter enters standby/shutdown mode, disabling the primary DC-to-AC power stage. When toggled ON, the inverter resumes normal grid-tied / off-grid power generation. Available in both **Basic** and **Full** modes.

#### `Audible Buzzer` (`buzzer_switch`)
* **Cloud Parameter:** `dspBeepOnOff`
* **Description:** Enables or mutes the internal audible buzzer on the inverter motherboard for keypress confirmations and fault/warning alerts.

#### `Anti-Backflow (Zero Export)` (`anti_backflow_switch`)
* **Cloud Parameter:** `localAntiBackflowEnable`
* **Description:** Controls zero-export protection. When enabled, the inverter curtails PV output to strictly match load demands and prevent feeding surplus power into the public electricity grid. On `AO-6KSL-G3`, power flow is measured via the RS485 Smart Meter.

#### `External CT Enable` (`ct_enable`)
* **Cloud Parameter:** `ctMode` (0 = Smart Meter / Disabled, 1 = CT Enabled)
* **Description:** Toggles external current measurement mode. On inverters with physical CT clamp terminals (`HSC`, `FSC`), this enables reading from the external CT clamp. On `AO-6KSL-G3`, setting this to 0 activates the RS485 Smart Meter.

#### `Overload to Bypass` (`overload_to_bypass`)
* **Cloud Parameter:** `overloadToBypass`
* **Description:** When continuous load demands exceed the inverter's rated continuous inverter power, this switch instructs the inverter to automatically transfer loads to AC utility grid bypass instead of tripping an overload fault.

#### `Zero Power Output` (`zero_current_enable`)
* **Cloud Parameter:** `zeroCurrentEnable`
* **Description:** Forces zero-current export buffer to avoid accidental reverse feed into high-sensitivity meters.

#### `VFRT Enable` (`vfrt_enable`)
* **Cloud Parameter:** `vfrtEnable`
* **Description:** Voltage and Frequency Ride-Through control for European grid code compliance.

#### `Generator Dry Contact` (`generator_dry_contact`)
* **Cloud Parameter:** `generatorDryContact`
* **Description:** Enables relay dry contact control on the motherboard to automatically crank or signal an external backup fuel generator when battery voltage drops below `batNeedChrVolt`.

#### `AC Grid Charging` (`ac_charge_enable_switch`)
* **Cloud Parameter:** `acChrEnable`
* **Description:** Allows or forbids the internal battery charger from drawing power from the utility AC grid.

#### `EPS Output` (`eps_enable_switch`)
* **Cloud Parameter:** `epsEnable`
* **Description:** Enables off-grid Emergency Power Supply (EPS) backup output when the utility grid fails.

#### `Bypass Mode` (`bypass_enable_switch`)
* **Cloud Parameter:** `bypassEnable`
* **Description:** Enables automatic internal static bypass routing AC grid power directly to loads.

#### `Generator Charging` (`gen_charge_enable_switch`)
* **Cloud Parameter:** `genChrEnable`
* **Description:** Allows the inverter to charge the battery bank using power delivered to the generator input port.

#### `Battery Equalization` (`equalization_switch`)
* **Cloud Parameter:** `batteryEqualization`
* **Description:** Activates periodic high-voltage equalization cycle for lead-acid battery banks to prevent sulfation.

#### `Force Full Charge` (`force_full_charge_switch`)
* **Cloud Parameter:** `forceFullCharge`
* **Description:** Overrides current priority schedule to immediately charge the battery bank to 100% SOC.

---

### 3.2 Buttons Platform

#### `Force Inverter Data Refresh` (`refresh_button`)
* **Description:** Requests immediate telemetry and parameter polling from the HaiPower cloud server.

#### `CT Calibration` (`ct_calibration`)
* **Cloud Register:** Register 96 = `1`
* **Hardware Availability:** HSC-3~8K, AH-SL-G2, FSC-8~12K, HSA-8~12K. *(Excluded on AO-6KSL-G3 which uses an RS485 Smart Meter)*.
* **Description:** Triggers zero-point calibration on external physical CT current clamps. Must be performed when inverter is running with zero load through the CT to calibrate offset bias.

#### `CT Detection` (`ct_detection`)
* **Cloud Register:** Register 96 = `2`
* **Hardware Availability:** HSC-3~8K, AH-SL-G2, FSC-8~12K, HSA-8~12K. *(Excluded on AO-6KSL-G3)*.
* **Description:** Triggers CT polarity and orientation detection. The inverter generates a test power pulse and checks whether the CT clamp measures positive or negative current flow, automatically setting CT orientation.

---

### 3.3 Select Platform (Operational Modes)

#### `Power Supply Priority` (`power_priority`)
* **Cloud Parameter:** `powerPriority`
* **Options:**
  1. `SOL (Solar/PV Priority)`: Solar energy powers loads first. If solar is insufficient, battery supplies remaining demand. Utility grid is only used when battery reaches low voltage cutoff.
  2. `UTI (Utility Priority)`: Utility grid powers loads as default. Solar and battery power are reserved for battery charging and power outages.
  3. `SBU (Solar-Battery-Utility Priority)`: Solar energy powers loads first. Battery provides power whenever solar is unavailable. Inverter switches to utility grid only when battery drops below `bat2acVolt` / `gridFirstStopSOC`.

#### `Charging Priority` (`charging_priority`)
* **Cloud Parameter:** `chargingPriority`
* **Options:**
  1. `CSO (Solar Priority)`: Solar energy charges battery first. Utility grid only charges battery when solar is completely unavailable.
  2. `SNU (Solar + Utility Hybrid)`: Solar and AC utility grid charge the battery concurrently up to the configured current limit.
  3. `OSO (Only Solar)`: Utility grid is completely forbidden from charging the battery, regardless of battery voltage.

#### `Grid Input Voltage Range` (`ac_input_type`)
* **Cloud Parameter:** `acInputMode`
* **Options:**
  1. `APL (Appliance Mode)`: Wide input voltage window (90V–280V AC), ideal for unstable rural grids and generators.
  2. `UPS (UPS Mode)`: Narrow input voltage window (170V–280V AC) with ultra-fast transfer time (<10ms) to protect sensitive computer equipment.

#### `GEN Port Work Mode` (`gen_port_mode`)
* **Cloud Parameter:** `genMode`
* **Options:**
  1. `Generator`: Port acts as an AC input for a fuel backup generator.
  2. `Microinverter / AC Input`: Port accepts AC input from secondary solar microinverters, performing AC-coupling.
  3. `Smart Load Output`: Port functions as an auxiliary output to power non-critical loads (e.g., heat pumps, water heaters, EV chargers) only when solar is surplus and battery SOC is high.

---

### 3.4 Numbers Platform (Inverter Settings)

#### Battery Charging Currents:
* **`Max Battery Charge Current`** (`intchargecurrentlimit`): Combined DC charging current limit (1A to 120A).
* **`AC Grid Charge Current`** (`acChargingCurrent`): Maximum charging current allowed from AC grid (1A to 100A).
* **`Generator Charge Current`** (`genChargeLimit`): Maximum charging current drawn from generator (1A to 120A).
* **`Generator Rated Power`** (`genInputPower`): Rated continuous power capacity of generator (100W to 10,000W).
* **`CT Current Ratio (1~3000)`** (`ctRatio`): Current transformer turns ratio (1~3000). *(Excluded on AO-6KSL-G3)*.

#### Battery Voltage Thresholds (48V Low-Voltage Profiles):
* **`Battery Charging CV Voltage`** (`vbatconstantcharge`): Absorption / Constant Voltage setpoint (48.0V to 59.2V).
* **`Battery Float Voltage`** (`uwFloatVLead100T`): Float trickle voltage setpoint (48.0V to 58.4V).
* **`Battery to Grid Voltage (SBU Mode)`** (`bat2acVolt`): Switch loads from battery to grid (44.0V to 52.0V).
* **`Grid to Battery Voltage (SBU Mode)`** (`ac2batVolt`): Switch loads from grid back to battery (48.0V to 58.0V).
* **`Battery Low-Voltage Cutoff`** (`vbatStopForDischarge`): Cutoff voltage where inverter stops discharging (40.0V to 48.0V).
* **`Battery Under-Voltage Alarm`** (`batUnderVoltPoint`): Audible alarm threshold (40.0V to 50.0V).
* **`Low-Voltage Recovery`** (`batLVBreakRestartVolt`): Battery voltage to resume inverter operation (50.0V to 58.0V).
* **`Battery Recharge Threshold`** (`batNeedChrVolt`): Voltage triggering generator dry-contact auto-start (50.0V to 56.0V).
* **`Over-Voltage Disconnect`** (`batHighVoltDisConPoint`): High voltage cutoff protecting electronics (50.0V to 62.0V).

#### Battery SOC Thresholds:
* **`On-Grid Discharge Cutoff SOC`** (`gridFirstStopSOC`): When grid is connected, battery discharge stops at this SOC level (10% to 90%).
* **`On-Grid Recovery SOC`** (`ubOPRecoverDischargeSOC`): SOC required before resuming discharge to grid loads (20% to 100%).
* **`Off-Grid Discharge Cutoff SOC`** (`offLineLoadFirstStopSoc`): In off-grid mode, emergency reserve cutoff (5% to 90%).
* **`Off-Grid Recovery SOC`** (`ubOffGridRecoverDischargeSOC`): SOC required to restart off-grid EPS loads (10% to 100%).
* **`Charging Cutoff SOC`** (`batFirststopSOC`): Target SOC where bulk charging terminates (50% to 100%).

#### Secondary / Smart Load Settings:
* **`Smart Load Cutoff SOC`** (`ubSecondLoadDisConSOC`): SOC threshold to disconnect secondary loads (10% to 100%).
* **`Smart Load Cutoff Voltage`** (`nonCriticlLoad_BatDisConVolt`): Battery voltage to disconnect secondary loads (42.0V to 54.0V).
* **`Smart Load Recovery SOC`** (`nonCriticlLoadRecorveSOC`): SOC required to re-enable smart load output (10% to 100%).
* **`Smart Load Recovery Voltage`** (`nonCriticlLoadRecorveVol`): Voltage required to re-enable smart load output (42.0V to 56.0V).

#### Grid & Power Rate Controls:
* **`Anti-Reverse Grid Compensation`** (`uwGridPowerCompensation`): Offset buffer (0W to 500W) to guarantee zero export.
* **`Active Power Rate Limit`** (`activePRate`): Inverter active power curtailment percentage (1% to 100%).

---

### 3.5 Sensors Platform (87 Entities)

* **Energy Dashboard:** `daily_pv_energy`, `total_pv_energy`, `daily_load_energy`, `total_load_energy`, `daily_grid_in_energy`, `total_grid_in_energy`, `daily_grid_out_energy`, `total_grid_out_energy`, `daily_battery_charge_energy`, `daily_battery_discharge_energy`, `total_battery_charge_energy`, `total_battery_discharge_energy`.
* **Real-Time Powers:** `pv_total_power`, `house_load_power`, `eps_output_power`, `battery_charging_power`, `battery_discharging_power`, `grid_active_power`, `extra_ac_power_to_grid`, `generator_active_power`, `generator_phase_r_power`.
* **Electrical Voltages & Currents:** `pv1_voltage`, `pv1_power`, `pv1_current`, `pv2_voltage`, `pv2_power`, `pv2_current`, `ac_voltage_phase_r`, `grid_current`, `eps_current`, `eps_apparent_power`, `grid_frequency`, `dc_bus_voltage`.
* **BMS & Battery Analytics:** `battery_type`, `battery_priority`, `battery_status`, `battery_voltage`, `battery_current`, `battery_max_charge_curr`, `battery_max_discharge_curr`, `battery_min_cell_voltage`, `battery_max_cell_voltage`, `battery_temperature`, `battery_rated_capacity`, `battery_charging_voltage`, `battery_module_count`, `battery_cell_count`, `battery_soc`, `battery_soh`.
* **Derived Averages & Predictive Analytics:** `battery_charge_eta`, `battery_soc_speed`, `battery_power_speed`, `avg_pv_power`, `avg_battery_power`, `avg_grid_power`, `avg_eps_load`, `avg_house_load`.
* **Diagnostics & Hardware:** `inverter_status`, `operation_mode`, `fault_code`, `fault_description`, `warn_code`, `warn_description`, `device_serial_number`, `data_logger_number`, `device_model`, `system_time`, `hardware_mode_code`, `arm_version`, `dsp_version`, `firmware_version`, `total_work_time`, `max_inverter_power`, `afci_value`, `ct_mode_status`, `ct_ratio_status`, `co2_reduction`, `tree_equivalent`, `last_telemetry_time`.
