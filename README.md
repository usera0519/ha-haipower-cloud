<p align="center">
  <img src="icon.png" alt="HaiPower Cloud Logo" width="160">
</p>

# HaiPower Cloud - Sandisolar / Aohai Solar Inverter Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/default)
[![Home Assistant](https://img.shields.io/badge/Home--Assistant-2024.1+-blue.svg)](https://www.home-assistant.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Home Assistant custom integration for **Sandisolar** and compatible **Aohai HiPower / HaiPower** solar hybrid inverters connected to the `eu.aohaidigitalpower.com` cloud platform.

---

> 📖 **Full Entity Reference & Compatibility Matrix**  
> For an in-depth explanation of every entity, calculation, setting threshold, and model-by-model compatibility breakdown, see the:  
> 👉 **[Detailed Entity Encyclopedia & Inverter Compatibility Matrix](docs/ENTITIES.md)**

---

> ⚠️ **Disclaimer**  
> This is an **unofficial, community-developed integration**. It is not affiliated with, sponsored by, or supported by Sandisolar, Aohai Digital Power, or the HaiPower cloud platform. All product names and trademarks belong to their respective owners.

---

## ☀️ Supported Inverter Families & Differences

Based on the official technical manuals, the HaiPower Cloud platform supports several inverter architectures:

1. **AO-6KSL-G3 / GSA-PRO Series (5kW / 6.2kW / 6.5kW)** *(Primary verified model)*  
   * **Phase & Battery:** Single-phase 230V AC with 48V Low-Voltage battery (40V–60V DC).
   * **Solar Input:** 1 high-current MPPT (up to 40A DC, 90–450V DC range, max Voc 500V DC).
   * **Outputs & Controls:** Dual AC outputs (Main UPS output + Smart Load second output with separate disconnect voltage/SOC thresholds), external CT clamp with programmable ratio (1~3000), zero-export anti-backflow, generator dry-contact auto-start, parallel up to 6 units.
2. **GSA-5-6.2K1P-BL Series (Standard Series)**  
   * **Phase & Battery:** Single-phase 230V AC, 48V Low-Voltage battery.
   * **Features:** Single AC output, front panel RGB status ring, off-grid and on-grid feed-in, CT/Meter support.
3. **SD-HYM-4862HWP Series (Outdoor Hybrid)**  
   * **Phase & Battery:** Single-phase 230V AC, 48V Low-Voltage battery, IP65 waterproof enclosure.
   * **Features:** Dual outputs (Full load + Smart load), parallel operation, generator dry contact, Wi-Fi logger.
4. **HSC-3-8K1P-BL Series (3kW – 8kW High-End Residential)**  
   * **Phase & Battery:** Single-phase 230V AC, 48V Low-Voltage battery.
   * **Solar Input:** Dual independent MPPT trackers (ideal for East-West roof configurations).
   * **Features:** <10ms UPS switchover, peak shaving, Time-of-Use (TOU) tariffs, microinverter AC coupling on GEN port.
5. **HTA-15-30K3P-BH Series (15kW – 30kW Commercial Three-Phase)**  
   * **Phase & Battery:** Three-phase 400V AC, High-Voltage Battery System (150V–800V DC).
   * **Solar Input:** 2 to 4 MPPT trackers (up to 1000V DC Voc, up to 45kW PV input).
   * **Features:** 100% unbalanced 3-phase output, dual EPS backup circuits, commercial 3-phase CT/Meter support.
6. **FSF-1.5-2K1P-BL Series (1.5kW – 2kW Compact Storage)**  
   * **Phase & Battery:** Single-phase 230V AC, 12V or 24V Low-Voltage battery.
   * **Features:** Designed for balcony solar, cabins, and mobile RV applications. Single MPPT (30–400V), single AC output.

---

## ⚡ Key Capabilities

* **100% Cloud-Native:** Works via Wi-Fi logger directly through `eu.aohaidigitalpower.com`. No Modbus RS485 converter or custom hardware required.
* **Automatic Captcha Resolution:** Authentication verification tokens are decoded automatically in the background—no manual captcha input.
* **Entity Mode Selection (Basic vs Full):**
  * **Basic Mode:** Lightweight profile exposing only essential sensors for Home Assistant Energy Dashboard, voltages, powers, operational status, fault/warn alarms, and the `Inverter Operation` switch.
  * **Full Mode:** Complete profile with all 87 sensors, 15 switches, 25 numbers, 4 selects, and 3 buttons (BMS cell diagnostics, moving averages, charge ETA, Smart Load shedding, generator controls, and CT buttons).
* **CT Calibration & Detection Buttons:** Directly trigger hardware CT calibration (`register 96=1`) and polarity detection (`register 96=2`) from Home Assistant.
* **Predictive Battery Analytics:** Real-time calculation of Battery Charge ETA, SOC speed (%/h), battery power dynamic speed (W/h), and 5-minute moving averages (AVG).

---

## 🔐 Platform Access Codes & Passwords

* **Web Portal & App Advanced Settings Password:** Calculated daily as `ah` + `YYYYMMDD` (e.g. `ah20261107`).
* **Remote Wake Up Code:** `666666`.
* **Inverter Physical LCD Service PIN:** `618`.

---

## 📦 Installation

### Method 1: Via HACS (Recommended)
1. Open Home Assistant $\rightarrow$ **HACS** $\rightarrow$ **Integrations**.
2. Click the top-right menu and choose **Custom repositories**.
3. Add `https://github.com/usera0519/ha-haipower-cloud` with category **Integration**.
4. Click **Download**, then restart Home Assistant.

### Method 2: Manual Installation
1. Download `ha-haipower-cloud.zip` from the latest release.
2. Unpack into your Home Assistant directory under:
   ```text
   /config/custom_components/haipower_cloud/
   ```
3. Restart Home Assistant.

---

## ⚙️ Configuration & Options

1. In Home Assistant, go to **Settings** $\rightarrow$ **Devices & Services** $\rightarrow$ **Add Integration**.
2. Search for **HaiPower Cloud**.
3. Enter your account email and password for `eu.aohaidigitalpower.com`.
4. Select your inverter (DSN) and choose between **Full** or **Basic** entity mode.
5. To adjust settings later (change entity mode or polling interval 10–300s), click **Configure** on the integration card.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
