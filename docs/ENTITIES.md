# HaiPower Cloud / Sandisolar - Comprehensive Entities Catalog & Model Compatibility

This document provides a complete technical explanation for all entities exposed by the `haipower_cloud` Home Assistant integration, based on the official technical manuals for **Aohai Digital Power**, **Sandisolar**, and OEM partner inverters.

---

## 1. Supported Inverter Families & Architectural Overview

Based on the engineering manuals located in the `manuals/` directory, the cloud platform (`eu.aohaidigitalpower.com`) communicates with multiple inverter series. Each family has specific hardware characteristics:

| Family / Series | Phase | Battery System | MPPT Count | AC Outputs | Key Features |
|---|---|---|---|---|---|
| **AO-6KSL-G3 / GSA-PRO** *(e.g. SD-PRO-EU 6.5K)* | 1-Phase (230V) | 48V Low Voltage (40–60V DC) | 1 High-Current (40A) | Dual (Main + Smart Load) | Anti-backflow CT (1~3000), Generator dry contact, parallel up to 6 units, AFCI |
| **GSA-5-6.2K1P-BL** *(Standard)* | 1-Phase (230V) | 48V Low Voltage (40–60V DC) | 1 High-Current (40A) | Single AC Output | Cost-effective hybrid, RGB ring indicator, CT/Meter support, off-grid & on-grid |
| **SD-HYM-4862HWP** | 1-Phase (230V) | 48V Low Voltage (40–60V DC) | 1 Wide-Range (60–500V) | Dual (Main + Smart Load) | IP65 outdoor enclosure, parallel operation, Smart Load shedding, built-in Wi-Fi |
| **HSC-3-8K1P-BL** | 1-Phase (230V) | 48V Low Voltage (40–60V DC) | 2 Independent MPPTs | Main + EPS Backup | Dual roof tracker, <10ms UPS switchover, peak shaving, Time-of-Use (TOU) tariffs |
| **HTA-15-30K3P-BH** | 3-Phase (400V) | High Voltage (150–800V DC) | 2–4 MPPTs (up to 1000V) | 3-Phase + Dual EPS | Commercial/Large residential, 100% unbalanced 3-phase output, dual EPS, 3-phase CT |
| **FSF-1.5-2K1P-BL** | 1-Phase (230V) | 12V / 24V Low Voltage | 1 MPPT (30–400V) | Single AC Output | Balcony / RV / Cabin storage, compact size, basic battery charging, no dual output |

> **Legend for Compatibility Table:**
> * `✓` = Fully supported and verified by hardware specification / register mapping.
> * `❌` = Not supported by this inverter hardware architecture (e.g., 3-phase voltage on single-phase inverter, Smart Load on single-output inverter).
> * `?` = Feature depends on specific hardware variant, installed optional board (such as AFCI module), or firmware release.

---

## 2. Inverter Model Compatibility Matrix

| Entity Name | Key | Type | Mode | AO-6KSL / GSA-PRO | GSA Standard | SD-HYM HWP | HSC 1P | HTA 3P | FSF 1P |
|---|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Inverter Operation** | `power_switch` | Switch | Basic/Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Audible Buzzer** | `buzzer_switch` | Switch | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Anti-Backflow (Zero Export)** | `anti_backflow_switch` | Switch | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ |
| **External CT Enable** | `ct_enable` | Switch | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ |
| **Overload to Bypass** | `overload_to_bypass` | Switch | Full | ✓ | ✓ | ✓ | ✓ | ? | ✓ |
| **Zero Power Output** | `zero_current_enable` | Switch | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ |
| **VFRT Enable** | `vfrt_enable` | Switch | Full | ✓ | ? | ? | ✓ | ✓ | ❌ |
| **Generator Dry Contact** | `generator_dry_contact` | Switch | Full | ✓ | ? | ✓ | ✓ | ✓ | ❌ |
| **AC Grid Charging** | `ac_charge_enable_switch` | Switch | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **EPS Output** | `eps_enable_switch` | Switch | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Bypass Mode** | `bypass_enable_switch` | Switch | Full | ✓ | ✓ | ✓ | ✓ | ? | ✓ |
| **Generator Charging** | `gen_charge_enable_switch` | Switch | Full | ✓ | ? | ✓ | ✓ | ✓ | ❌ |
| **Battery Equalization** | `equalization_switch` | Switch | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Force Full Charge** | `force_full_charge_switch` | Switch | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Bluetooth Broadcast** | `bluetooth_switch` | Switch | Full | ✓ | ✓ | ? | ? | ? | ? |
| **Force Inverter Data Refresh** | `refresh_button` | Button | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **CT Calibration** | `ct_calibration` | Button | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ |
| **CT Detection** | `ct_detection` | Button | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ |
| **Power Supply Priority** | `power_priority` | Select | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Charging Priority** | `charging_priority` | Select | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Grid Input Voltage Range** | `ac_input_type` | Select | Full | ✓ | ✓ | ✓ | ✓ | ? | ✓ |
| **GEN Port Work Mode** | `gen_port_mode` | Select | Full | ✓ | ? | ✓ | ✓ | ✓ | ❌ |
| **Max Battery Charge Current** | `max_battery_charge_current` | Number | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **AC Grid Charge Current** | `ac_charging_current_limit` | Number | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Generator Charge Current** | `generator_charging_current_limit`| Number | Full | ✓ | ? | ✓ | ✓ | ✓ | ❌ |
| **Generator Rated Power** | `generator_input_power` | Number | Full | ✓ | ? | ✓ | ✓ | ✓ | ❌ |
| **CT Current Ratio (1~3000)** | `ct_current_ratio` | Number | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ |
| **Battery Charging CV Voltage** | `vbat_constant_charge` | Number | Full | ✓ | ✓ | ✓ | ✓ | ❌ (HV) | ✓ (12V scaled) |
| **Battery Float Voltage** | `vbat_floating_charge` | Number | Full | ✓ | ✓ | ✓ | ✓ | ❌ (HV) | ✓ (12V scaled) |
| **Battery to Grid Voltage (SBU)** | `bat2ac_volt` | Number | Full | ✓ | ✓ | ✓ | ✓ | ❌ (HV) | ✓ (12V scaled) |
| **Grid to Battery Voltage (SBU)** | `ac2bat_volt` | Number | Full | ✓ | ✓ | ✓ | ✓ | ❌ (HV) | ✓ (12V scaled) |
| **Battery Low-Voltage Cutoff** | `vbat_stop_discharge` | Number | Full | ✓ | ✓ | ✓ | ✓ | ❌ (HV) | ✓ (12V scaled) |
| **Battery Under-Voltage Alarm** | `bat_undervolt_alarm` | Number | Full | ✓ | ✓ | ✓ | ✓ | ❌ (HV) | ✓ (12V scaled) |
| **Low-Voltage Recovery** | `bat_lv_restart_volt` | Number | Full | ✓ | ✓ | ✓ | ✓ | ❌ (HV) | ✓ (12V scaled) |
| **Battery Recharge Threshold** | `bat_need_charge_volt` | Number | Full | ✓ | ✓ | ✓ | ✓ | ❌ (HV) | ✓ (12V scaled) |
| **Over-Voltage Disconnect** | `bat_overvolt_disconnect` | Number | Full | ✓ | ✓ | ✓ | ✓ | ❌ (HV) | ✓ (12V scaled) |
| **On-Grid Discharge Cutoff SOC** | `grid_first_stop_soc` | Number | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ? |
| **On-Grid Recovery SOC** | `grid_recover_soc` | Number | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ? |
| **Off-Grid Discharge Cutoff SOC**| `offline_stop_soc` | Number | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ? |
| **Off-Grid Recovery SOC** | `offline_recover_soc` | Number | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ? |
| **Charging Cutoff SOC** | `charging_cutoff_soc` | Number | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ? |
| **Smart Load Cutoff SOC** | `smart_load_cutoff_soc` | Number | Full | ✓ | ❌ | ✓ | ? | ✓ | ❌ |
| **Smart Load Cutoff Voltage** | `smart_load_cutoff_volt` | Number | Full | ✓ | ❌ | ✓ | ? | ❌ (HV) | ❌ |
| **Smart Load Recovery SOC** | `smart_load_recover_soc` | Number | Full | ✓ | ❌ | ✓ | ? | ✓ | ❌ |
| **Smart Load Recovery Voltage** | `smart_load_recover_volt` | Number | Full | ✓ | ❌ | ✓ | ? | ❌ (HV) | ❌ |
| **Anti-Reverse Grid Compensation**| `grid_power_compensation`| Number | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ |
| **Active Power Rate Limit** | `active_power_rate` | Number | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **PV Total Power** | `pv_total_power` | Sensor | Basic/Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **House Load Power** | `house_load_power` | Sensor | Basic/Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **EPS Backup Load Power** | `eps_output_power` | Sensor | Basic/Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Battery Charging Power** | `battery_charging_power` | Sensor | Basic/Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Battery Discharging Power** | `battery_discharging_power`| Sensor | Basic/Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Grid Active Power** | `grid_active_power` | Sensor | Basic/Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Grid Export Power** | `extra_ac_power_to_grid` | Sensor | Basic/Full | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ |
| **Generator Active Power** | `generator_active_power` | Sensor | Basic/Full | ✓ | ? | ✓ | ✓ | ✓ | ❌ |
| **Battery Voltage & Current** | `battery_voltage`/`current` | Sensor | Basic/Full | ✓ | ✓ | ✓ | ✓ | ✓ (HV) | ✓ |
| **Battery SOC & Temperature** | `battery_soc`/`temp` | Sensor | Basic/Full | ✓ | ✓ | ✓ | ✓ | ✓ | ? |
| **PV1 Voltage & Current** | `pv1_voltage`/`current` | Sensor | Basic/Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **PV2 Voltage & Current** | `pv2_voltage`/`current` | Sensor | Basic/Full | ? (Dual string) | ? | ? | ✓ | ✓ | ❌ |
| **Grid Frequency & Voltage** | `grid_frequency`/`voltage`| Sensor | Basic/Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Energy Dashboard Statistics** | `daily_pv_energy`, etc. | Sensor | Basic/Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Moving Averages (AVG 5m)** | `avg_pv_power`, etc. | Sensor | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Battery ETA & Speed** | `battery_charge_eta`, etc. | Sensor | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **AFCI Arc Detector Value** | `afci_value` | Sensor | Full | ? (with AFCI) | ? | ? | ? | ✓ | ❌ |
| **CT Mode & Ratio Status** | `ct_mode`/`ratio_status` | Sensor | Full | ✓ | ✓ | ✓ | ✓ | ✓ | ❌ |

---

## 3. Detailed Entity Encyclopedia

### 3.1 Switches Platform

#### `Inverter Operation` (`power_switch`)
* **Cloud Parameter:** `onOff` / `inveterOnOff` / `onoff`
* **Available in Basic Mode:** Yes
* **Description:** Master electronic switch controlling whether the inverter stage is active or stopped. When turned OFF, the inverter stops generating AC power and disconnects from supplying the loads, but the internal MPPT charger continues charging the battery if solar power is available. Turning ON activates inverter conversion and power delivery.

#### `Audible Buzzer` (`buzzer_switch`)
* **Cloud Parameter:** `dspBeepOnOff`
* **Description:** Controls the internal piezo buzzer alarm inside the inverter. When enabled, the inverter emits audible beeps upon button clicks, power state transitions, overload warnings, or fault conditions. Disabling it silences all routine and warning beeps.

#### `Anti-Backflow (Zero Export)` (`anti_backflow_switch`)
* **Cloud Parameter:** `localAntiBackflowEnable`
* **Description:** Activates the local anti-backflow function (Zero Export to Grid). When enabled, the inverter dynamically throttles solar power output and battery discharge to ensure zero electrical power is fed back into the public grid. Requires an external Current Transformer (CT) or energy meter installed at the main grid connection point.

#### `External CT Enable` (`ct_enable`)
* **Cloud Parameter:** `ctMode` (0 = Meter / Disabled, 1 = CT Enabled)
* **Description:** Selects the external grid sensing device between an RS485 energy meter (Modbus RTU) and an analog Current Transformer (CT clamp). Enabling this instructs the DSP to read grid import/export directly from the CT port.

#### `Overload to Bypass` (`overload_to_bypass`)
* **Cloud Parameter:** `overloadToBypass`
* **Description:** In battery mode, if the home load exceeds the inverter's rated continuous power capacity (e.g., >6000W), this setting automatically transfers the load to grid bypass without cutting off power. Once load drops to normal levels, the inverter returns to battery power.

#### `Zero Power Output` (`zero_current_enable`)
* **Cloud Parameter:** `zeroCurrentEnable`
* **Description:** Extreme zero-export protection setting. While normal anti-backflow allows micro-second power fluctuations, zero power output enforces a strict negative export margin to prevent any reverse energy flow on sensitive digital grid meters.

#### `VFRT Enable` (`vfrt_enable`)
* **Cloud Parameter:** `vfrtEn`
* **Description:** Voltage Fault Ride-Through (VFRT) stabilization setting. Mandated by certain European grid codes (e.g., EN 50549 / VDE-AR-N 4105), this enables the inverter to remain connected during brief grid voltage dips instead of immediately disconnecting.

#### `Generator Dry Contact` (`generator_dry_contact`)
* **Cloud Parameter:** `dryControl`
* **Description:** Controls the dry contact relay terminals (NC/NO) used to signal an external auto-start generator or turn on an external contactor when battery voltage drops below the recharge threshold.

#### `AC Grid Charging` (`ac_charge_enable_switch`)
* **Cloud Parameter:** `acchargeEn` / `ubAcChargeEnable`
* **Description:** Allows or blocks charging the battery from the utility AC grid. When turned off, the battery will strictly charge from solar PV power (or generator, if enabled), preventing utility electricity consumption for battery charging.

#### `EPS Output` (`eps_enable_switch`)
* **Cloud Parameter:** `epSEn`
* **Description:** Controls the Emergency Power Supply (EPS / Backup) output port. When disabled, the backup output is cut off even during grid outages. Must be enabled to provide uninterruptible power to critical backup circuits.

#### `Bypass Mode` (`bypass_enable_switch`)
* **Cloud Parameter:** `bypassEn`
* **Description:** Allows the inverter to directly connect the utility AC grid to the loads (Bypass mode) whenever solar and battery power are depleted or when the inverter is in standby.

#### `Generator Charging` (`gen_charge_enable_switch`)
* **Cloud Parameter:** `genChargeEn`
* **Description:** Enables battery charging using power supplied to the GEN input port from a diesel/gasoline generator or microinverter AC input.

#### `Battery Equalization` (`equalization_switch`)
* **Cloud Parameter:** `equalization`
* **Description:** Manually initiates or enables periodic battery equalization charging (mainly for Lead-Acid, flooded, or AGM battery types) to balance individual cell voltages and remove lead sulfation.

#### `Force Full Charge` (`force_full_charge_switch`)
* **Cloud Parameter:** `ubForceChargeEnable` / `forceFullCharge`
* **Description:** Forces the inverter to immediately charge the connected battery bank to 100% SOC from any available source (solar and grid). Used prior to forecasted grid outages or storms.

#### `Bluetooth Broadcast` (`bluetooth_switch`)
* **Cloud Parameter:** `ubBluetoothEn`
* **Description:** Enables or disables the local Bluetooth low-energy (BLE) radio on the inverter front panel, preventing unauthorized local device pairing.

---

### 3.2 Buttons Platform

#### `Force Inverter Data Refresh` (`refresh_button`)
* **Action:** Triggers an immediate HTTP polling refresh to retrieve the latest cloud telemetry and parameters without waiting for the scheduled scan interval.

#### `CT Calibration` (`ct_calibration`)
* **Action:** Calls cloud API register `96=1` (`view/hard/setOneRegister`). Instructs the inverter DSP to calibrate zero-offset and phase angle on the external CT clamp. Should be pressed during initial commissioning when loads are stable.

#### `CT Detection` (`ct_detection`)
* **Action:** Calls cloud API register `96=2` (`view/hard/setOneRegister`). Runs an automated CT wiring direction and polarity check. The inverter verifies whether the CT clamp is pointing towards the grid or the load, preventing reverse reading errors.

---

### 3.3 Selects Platform

#### `Power Supply Priority` (`power_priority`)
* **Cloud Parameter:** `periodpower`
* **Options:**
  1. `SOL (Solar/PV Priority)`: Solar energy powers loads first. If solar is insufficient, battery supplies remaining demand. Grid only supplies loads when battery drops to low voltage/cutoff SOC.
  2. `UTI (Utility Priority)`: Utility grid powers loads as first priority. Solar and battery only charge the battery or support loads during grid blackout.
  3. `SBU (Solar-Battery-Utility Priority)`: Solar energy powers loads first. Battery provides power whenever solar is unavailable. Utility grid only intervenes when battery reaches the Low-Voltage Cutoff threshold.

#### `Charging Priority` (`charging_priority`)
* **Cloud Parameter:** `periodcharge`
* **Options:**
  1. `CSO (Solar Priority)`: Solar charges the battery first. Utility grid only charges the battery when solar is completely unavailable (e.g. nighttime).
  2. `SNU (Solar + Utility Hybrid)`: Solar and utility grid charge the battery simultaneously, maximizing battery recharge speed.
  3. `OSO (Only Solar)`: Solar energy is the only source allowed to charge the battery, regardless of grid availability.

#### `Grid Input Voltage Range` (`ac_input_type`)
* **Cloud Parameter:** `acInputType`
* **Options:**
  1. `APL (Appliance - Wide 90-280V)`: Wide AC input acceptance range (90V~280V). Best suited for unstable rural grids or standard household appliances.
  2. `UPS (UPS - Narrow 170-280V)`: Narrow AC input acceptance range (170V~280V) with fast (<10ms) transfer time, protecting sensitive IT equipment, servers, and computers from brownouts.

#### `GEN Port Work Mode` (`gen_port_mode`)
* **Cloud Parameter:** `genMode`
* **Options:**
  1. `Generator`: The port acts as an AC input for a fuel backup generator.
  2. `Microinverter / AC Input`: The port accepts AC power from secondary solar microinverters, performing AC-coupling.
  3. `Smart Load Output`: The port functions as an auxiliary output to power non-critical loads (e.g., heat pumps, water heaters, EV chargers) only when solar is surplus and battery SOC is high.

---

### 3.4 Numbers Platform (Inverter Settings)

#### Battery Charging Currents:
* **`Max Battery Charge Current`** (`intchargecurrentlimit`): Maximum combined DC charging current delivered to the battery (1A to 120A).
* **`AC Grid Charge Current`** (`acChargingCurrent`): Maximum charging current allowed from the utility AC grid (1A to 100A).
* **`Generator Charge Current`** (`genChargeLimit`): Maximum charging current drawn from the generator port (1A to 120A).
* **`Generator Rated Power`** (`genInputPower`): Rated continuous power capacity of the attached generator (100W to 10,000W).
* **`CT Current Ratio (1~3000)`** (`ctRatio`): The current transformer turns ratio (e.g., `100` for 100A:50mA CT, or `3000` for 3000:1 CT).

#### Battery Voltage Thresholds:
* **`Battery Charging CV Voltage`** (`vbatconstantcharge`): Absorption / Constant Voltage setpoint for battery charging (48.0V to 59.2V).
* **`Battery Float Voltage`** (`uwFloatVLead100T`): Trickle / Float voltage setpoint once battery reaches 100% (48.0V to 58.4V).
* **`Battery to Grid Voltage (SBU Mode)`** (`bat2acVolt`): In SBU mode, voltage threshold where inverter switches loads back to utility grid (44.0V to 52.0V).
* **`Grid to Battery Voltage (SBU Mode)`** (`ac2batVolt`): In SBU mode, voltage threshold where inverter returns from grid to battery power (48.0V to 58.0V).
* **`Battery Low-Voltage Cutoff`** (`vbatStopForDischarge`): Cutoff voltage where inverter stops discharging battery to prevent cell damage (40.0V to 48.0V).
* **`Battery Under-Voltage Alarm`** (`batUnderVoltPoint`): Threshold where inverter triggers audible warning and alarm (40.0V to 50.0V).
* **`Low-Voltage Recovery`** (`batLVBreakRestartVolt`): Battery voltage required before re-enabling inverter output after an empty shutdown (50.0V to 58.0V).
* **`Battery Recharge Threshold`** (`batNeedChrVolt`): Voltage threshold triggering dry contact auto-start for generator charging (50.0V to 56.0V).
* **`Over-Voltage Disconnect`** (`batHighVoltDisConPoint`): High voltage cutoff protecting electronics from battery overvoltage spikes (50.0V to 62.0V).

#### Battery SOC Thresholds:
* **`On-Grid Discharge Cutoff SOC`** (`gridFirstStopSOC`): When grid is connected, battery discharge stops at this SOC level (10% to 90%).
* **`On-Grid Recovery SOC`** (`ubOPRecoverDischargeSOC`): Battery SOC required before resuming discharge to grid-tied loads (20% to 100%).
* **`Off-Grid Discharge Cutoff SOC`** (`offLineLoadFirstStopSoc`): In off-grid islanding mode, battery cutoff SOC to preserve emergency reserve (5% to 90%).
* **`Off-Grid Recovery SOC`** (`ubOffGridRecoverDischargeSOC`): Battery SOC required to restart off-grid EPS loads (10% to 100%).
* **`Charging Cutoff SOC`** (`batFirststopSOC`): Target SOC where bulk charging terminates (50% to 100%).

#### Secondary / Smart Load Settings:
* **`Smart Load Cutoff SOC`** (`ubSecondLoadDisConSOC`): SOC threshold to disconnect secondary non-critical loads (10% to 100%).
* **`Smart Load Cutoff Voltage`** (`nonCriticlLoad_BatDisConVolt`): Battery voltage to disconnect secondary loads (42.0V to 54.0V).
* **`Smart Load Recovery SOC`** (`nonCriticlLoadRecorveSOC`): SOC required to re-enable smart load output (10% to 100%).
* **`Smart Load Recovery Voltage`** (`nonCriticlLoadRecorveVol`): Voltage required to re-enable smart load output (42.0V to 56.0V).

#### Grid & Power Rate Controls:
* **`Anti-Reverse Grid Compensation`** (`uwGridPowerCompensation`): Power offset buffer (0W to 500W) maintained to guarantee zero grid export.
* **`Active Power Rate Limit`** (`activePRate`): Inverter active power output curtailment percentage (1% to 100%).

---

### 3.5 Sensors Platform (87 Entities)

* **Energy Dashboard:** `daily_pv_energy`, `total_pv_energy`, `daily_load_energy`, `total_load_energy`, `daily_grid_in_energy`, `total_grid_in_energy`, `daily_grid_out_energy`, `total_grid_out_energy`, `daily_battery_charge_energy`, `daily_battery_discharge_energy`, `total_battery_charge_energy`, `total_battery_discharge_energy`.
* **Real-Time Powers:** `pv_total_power`, `house_load_power`, `eps_output_power`, `battery_charging_power`, `battery_discharging_power`, `grid_active_power`, `extra_ac_power_to_grid`, `generator_active_power`, `generator_phase_r_power`.
* **Electrical Voltages & Currents:** `pv1_voltage`, `pv1_power`, `pv1_current`, `pv2_voltage`, `pv2_power`, `pv2_current`, `ac_voltage_phase_r`, `grid_current`, `eps_current`, `eps_apparent_power`, `grid_frequency`, `dc_bus_voltage`.
* **BMS & Battery Analytics:** `battery_type`, `battery_priority`, `battery_status`, `battery_voltage`, `battery_current`, `battery_max_charge_curr`, `battery_max_discharge_curr`, `battery_min_cell_voltage`, `battery_max_cell_voltage`, `battery_temperature`, `battery_rated_capacity`, `battery_charging_voltage`, `battery_module_count`, `battery_cell_count`, `battery_soc`, `battery_soh`.
* **Derived Averages & Predictive Analytics:** `battery_charge_eta`, `battery_soc_speed`, `battery_power_speed`, `avg_pv_power`, `avg_battery_power`, `avg_grid_power`, `avg_eps_load`, `avg_house_load`.
* **Diagnostics & Hardware:** `inverter_status`, `operation_mode`, `fault_code`, `fault_description`, `warn_code`, `warn_description`, `device_serial_number`, `data_logger_number`, `device_model`, `system_time`, `hardware_mode_code`, `arm_version`, `dsp_version`, `firmware_version`, `total_work_time`, `max_inverter_power`, `afci_value`, `ct_mode_status`, `ct_ratio_status`, `co2_reduction`, `tree_equivalent`, `last_telemetry_time`.
