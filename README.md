<p align="center">
  <img src="icon.png" alt="HaiPower Cloud Logo" width="160">
</p>

# HaiPower Cloud - Sandisolar / Aohai Solar Inverter Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/default)
[![Home Assistant](https://img.shields.io/badge/Home--Assistant-2024.1+-blue.svg)](https://www.home-assistant.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Home Assistant custom integration for **Sandisolar** and compatible **Aohai HiPower / HaiPower** solar hybrid inverters connected to the `eu.aohaidigitalpower.com` cloud platform.

---

> ⚠️ **Disclaimer**  
> This is an **unofficial, community-developed integration**. It is not affiliated with, sponsored by, endorsed by, or supported by Sandisolar, Aohai Digital Power, or the HaiPower cloud platform. All product names, trademarks, and registered trademarks belong to their respective owners.

> ℹ️ **Hardware Testing & Compatibility Notice**  
> This integration has been **tested and verified exclusively on the Sandisolar SD-PRO-EU 6.5K Hybrid Solar Inverter (Model AO-6KSL-G3)** running with the HaiPower cloud data-logger.  
> Other power ratings and models in the Sandisolar / Aohai family (e.g. 3.6K, 5K, 6K, 8K, 10K, 12K) may also function properly if they utilize the same HaiPower cloud interface, but have not been directly tested by the author.

---

## ⚡ How This Integration Works

The integration connects directly to the official HaiPower platform (`eu.aohaidigitalpower.com`) using your account credentials:
* **Automatic Captcha Resolution:** Authentication verification tokens are decoded automatically in the background—no manual captcha solving, image recognition, or OCR is required.
* **Auto-Discovery:** Automatically scans your account for all associated solar stations and inverters, allowing you to select your device and assign a custom friendly name during setup.
* **Bi-directional Controls:** Sends parameter updates and operational commands (turn on/standby, charging priorities, voltage and current limits, anti-backflow, smart load cut-offs) directly to the inverter.

---

## 🔐 Platform Access Codes & Passwords

During analysis of the official HaiPower platform interface, the following access passwords and validation algorithms were identified:

### 1. Web Portal & Mobile App "Advanced Settings" Password
When accessing **Advanced Settings** in the HaiPower web portal or mobile application, a daily password is required. The password is generated client-side using the local date:
$$\text{Password} = \text{"ah"} + \text{YYYYMMDD}$$

* **Examples:**
  * If the date is `2026-11-05` $\rightarrow$ Password is `ah20261105`
  * If the date is `2026-11-06` $\rightarrow$ Password is `ah20261106`

### 2. Web Portal "Remote Wake Up" Code
* Master wake-up PIN: **`666666`**

### 3. Inverter Physical LCD Hardware Password
* For on-screen physical LCD settings (such as restoring factory settings or configuring anti-reverse grid feed power as described in the user manual):
  * Service PIN: **`618`**

---

## 🚀 Available Entities & Features

### 1. Home Assistant Energy Dashboard Compatibility
* **Real-Time Power:** PV Generation Power, House Load Consumption Power, Inverter Output Power, EPS Backup Power, Battery Charge & Discharge Power, Grid Active Import/Export Power.
* **Energy Accumulators:**
  * Daily & Total PV Energy Generated (`epVAllToday`, `epvTotal`)
  * Daily & Total House Load Energy Consumed (`eloadToday`, `eloadTotal`)
  * Daily & Total Grid Energy Imported (`efromGridToday`, `efromGridTotal`)
  * Daily & Total Grid Energy Exported (`etoGridToday`, `etoGridTotal`)
  * Daily & Total Battery Charge & Discharge Energy (`echargeToday`, `edischargeToday`, `echargeTotal`, `edischargeTotal`)

### 2. Status & Hardware Diagnostics
* **Inverter Status:** Real-time state (`ByPass`, `Standby`, `Normal`, `Fault`).
* **Operation Mode:** Current running mode (`PV Priority Mode (SOL)`, `Mains Priority Mode (UTI)`, `Inverter Priority Mode (SBU)`, `Grid Output Mode`).
* **Fault Diagnostics:** Master and Slave fault codes with clear text descriptions (e.g. `Normal (No Fault)`, `BMS fault`, `Fan fault`, `PV overvoltage`, `Inverter DC offset too high`).
* **Warning Diagnostics:** Master and Slave warning codes with descriptive text (e.g. `Normal (No Warning)`, `Low battery`, `Grid unavailable`).
* **Device Information:** Serial Number (DSN), Data Logger Number (CSN), Device Model, System Time, Total Work Time, Hardware Mode string, ARM Software Version, DSP Software Version, Firmware Version.

### 3. Battery Detailed Information
* **Type & Priority:** Battery Type (`Lead-acid Battery`, `Lithium Battery`, `Li-ion Battery (No Comm)`), Battery Priority (`Load Priority`, `Battery Priority`, etc.), Battery Status (`Charging`, `Discharging`, `Standby`).
* **Live Telemetry:** Voltage (V), Current (A), State of Charge (SOC %), State of Health (SOH %), Battery Temperature (°C).
* **BMS Limits & Health:** Max Charge Current (A), Max Discharge Current (A), Min & Max Cell Voltages (V), BMS Charging Constant Voltage (V), Rated Capacity (Ah), Number of Modules & Cells.

### 4. Interactive Controls & Parameter Configuration
* **Select Entities:**
  * `Power Supply Priority`: `SOL (PV Priority)`, `UTI (Mains Priority)`, `SBU (Inverter Priority)`
  * `Charging Priority`: `CSO (PV Priority)`, `SNU (Hybrid Charging)`, `OSO (PV Only Charging)` *(note: user manual typo 'OSS' is corrected to 'OSO' as used in inverter firmware)*
  * `Grid Input Mode`: `APL (Wide 90-280V)`, `UPS (Narrow 170-265V)`
* **Switch Entities:**
  * `Inverter Operation (On/Off)` (Run / Standby)
  * `Audible Buzzer Switch` (Mute / Unmute beeper)
  * `Anti-Backflow Switch` (Enable / Disable zero-export)
  * `Bluetooth Broadcast Switch`
  * `AC Grid Charging Enablement`
  * `EPS Backup Output Enable`
  * `Bypass Output Enable`
  * `Generator Charging Enable`
  * `Battery Equalization Enable`
  * `Force Full Battery Charging Enable`
* **Number Configuration Entities:**
  * `Maximum Battery Charging Current` (1 – 120 A)
  * `AC Battery Charging Current Limit` (1 – 100 A)
  * `Generator Charging Current Limit` (1 – 120 A)
  * `Battery Charging CV Voltage` (48.0 – 59.2 V)
  * `Float Charging Voltage` (48.0 – 58.4 V)
  * `Battery-to-Grid Voltage` (44.0 – 52.0 V)
  * `Grid-to-Battery Voltage` (48.0 – 58.0 V)
  * `Battery Low-Voltage Shutdown Voltage` (40.0 – 48.0 V)
  * `Battery Under-Voltage Alarm Threshold` (40.0 – 50.0 V)
  * `Low-Voltage Recovery Threshold` (50.0 – 58.0 V)
  * `Battery Recharging Recovery Threshold` (50.0 – 56.0 V)
  * `Battery Over-Voltage Disconnect Point` (50.0 – 62.0 V)
  * `On-Grid Discharge Cutoff SOC` (10 – 90 %)
  * `On-Grid End-of-Discharge Recovery SOC` (20 – 100 %)
  * `Off-Grid Discharge Cutoff SOC` (5 – 90 %)
  * `Off-Grid End-of-Discharge Recovery SOC` (10 – 100 %)
  * `Charging Cut-off SOC` (50 – 100 %)
  * `Non-Critical Load Disconnection BAT SOC` (10 – 100 %)
  * `Non-Critical Load Disconnection BAT Voltage` (42.0 – 54.0 V)
  * `Non-Critical Load Recovery BAT SOC` (10 – 100 %)
  * `Non-Critical Load Recovery BAT Voltage` (42.0 – 56.0 V)
  * `Anti-Reverse Mains Power Compensation` (0 – 300 W)
  * `Active Power Rate Limit` (1 – 100 %)
* **Button Entity:**
  * `Force Inverter Data Refresh`

---

## 📦 Installation

### Method 1: Via HACS (Recommended)
1. Open Home Assistant and navigate to **HACS** $\rightarrow$ **Integrations**.
2. Click the three dots in the top right corner and select **Custom repositories**.
3. Enter the repository URL: `https://github.com/usera0519/ha-haipower-cloud`
4. Set the Category to **Integration**.
5. Click **Download**, then restart Home Assistant.

### Method 2: Manual Installation
1. Download `ha-haipower-cloud.zip` from the latest release.
2. Unpack the zip file into your Home Assistant installation folder under:
   ```text
   /config/custom_components/haipower_cloud/
   ```
3. Restart Home Assistant.

---

## ⚙️ Setup & Configuration

1. In Home Assistant, go to **Settings** $\rightarrow$ **Devices & Services**.
2. Click **Add Integration** and search for **HaiPower Cloud**.
3. **Step 1:** Enter your email and password for the HaiPower platform (`eu.aohaidigitalpower.com`).
4. **Step 2:** Select your inverter from the discovered devices dropdown and assign your preferred friendly name (e.g. *Sandisolar Inverter*).
5. Submit the form—all sensors, switches, numbers, and selectors will be initialized immediately.

---

## 🛠️ Fault & Warning Reference Table

| Code | Type | Description |
|---|---|---|
| **0** | All | Normal / No fault / No warning |
| **103** | Fault | Inverter DC offset too high |
| **105** | Fault | Bypass AC output overloaded |
| **200** | Fault | Off-grid output voltage too low |
| **201** | Fault | Off-grid output voltage too high |
| **202** | Fault | Off-grid output short circuit |
| **203** | Fault | Off-grid output overloaded |
| **204** | Fault | Abnormal off-grid DC component offset |
| **301** | Fault | Battery open circuit |
| **305** | Fault | Battery overvoltage |
| **306** | Fault | Battery overcurrent |
| **307** | Fault | Battery communication fault |
| **308** | Fault | BMS fault |
| **400** | Fault | PV overvoltage |
| **403** | Fault | PV short circuit |
| **404** | Fault | PV reverse connection |
| **500** | Fault | Abnormal BUS voltage |
| **501** | Fault | Abnormal BUS voltage sampling |
| **502** | Fault | Abnormal internal device communication |
| **505** | Fault | Abnormal temperature sensor connection |
| **506** | Fault | Device over-temperature |
| **507** | Fault | Abnormal relay |
| **509** | Fault | Anti-counter-current output timeout |
| **510** | Fault | Mismatched software version |
| **511** | Fault | Fan fault |
| **513** | Fault | Parallel abnormality |
| **103** | Warning | Grid unavailable |
| **104** | Warning | Overrange voltage of grid |
| **105** | Warning | Overrange frequency of grid |
| **106** | Warning | No output voltage from generator |
| **107** | Warning | Overrange output voltage of generator |
| **108** | Warning | Overrange output frequency of generator |
| **302** | Warning | Low battery |
| **304** | Warning | Abnormal BMS information |
| **305** | Warning | Low battery voltage alarm |
| **502** | Warning | Abnormal memory reading and writing |

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
