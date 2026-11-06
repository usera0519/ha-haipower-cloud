"""DataUpdateCoordinator for Aohai HaiPower / Sandisolar integration."""
import logging
import datetime
from collections import deque
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .api import AohaiApiClient, AohaiApiError

_LOGGER = logging.getLogger(__name__)

class AohaiDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Aohai inverter data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: AohaiApiClient,
        dsn: str,
        csn: str,
        device_name: str,
        model_name: str = "SD-PRO-EU 6.5K",
        addr: int = 1,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
        config_entry = None,
    ):
        """Initialize the coordinator."""
        self.client = client
        self.dsn = dsn
        self.csn = csn
        self.device_name = device_name
        self.model_name = model_name
        self.addr = addr
        self.config_entry = config_entry
        
        # History buffers for rolling averages (last 10 samples)
        self.pv_history = deque(maxlen=10)
        self.battery_history = deque(maxlen=10)
        self.grid_history = deque(maxlen=10)
        self.eps_history = deque(maxlen=10)
        self.load_history = deque(maxlen=10)

        # ETA and speed tracking
        self.last_soc = None
        self.last_soc_time = None
        self.soc_speed = 0.0
        self.last_battery_power = None
        self.power_speed = 0.0

        # Ring buffer for recent diagnostic logs (last 20 messages)
        self.recent_logs = deque(maxlen=20)
        self._add_log("Inicjalizacja koordynatora HaiPower Cloud.")

        super().__init__(
            hass,
            _LOGGER,
            name=f"{device_name} ({dsn})",
            update_interval=timedelta(seconds=scan_interval),
        )

    def _add_log(self, message: str) -> None:
        """Add a timestamped log entry."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.recent_logs.append(f"[{timestamp}] {message}")

    def get_recent_logs_formatted(self) -> str:
        """Return formatted string of recent logs."""
        if not self.recent_logs:
            return "Brak zarejestrowanych zdarzeń."
        return "\n".join(reversed(self.recent_logs))

    async def _async_update_data(self):
        """Fetch real-time data, detailed info, and settings from Aohai API."""
        try:
            device_info = await self.hass.async_add_executor_job(
                self.client.get_device_info, self.dsn
            )
            params_info = await self.hass.async_add_executor_job(
                self.client.get_params_info, self.dsn
            )
            detailed_info = await self.hass.async_add_executor_job(
                self.client.get_detailed_info, self.dsn
            )

            # Perform real-time derived calculations
            now = datetime.datetime.now()
            
            # 1. Currents & Apparent Power
            vpv1 = float(device_info.get("vpv1") or 0.0)
            ppv1 = float(device_info.get("ppv1") or 0.0)
            pv1_current = round(ppv1 / vpv1, 2) if vpv1 > 10.0 else 0.0

            vpv2 = float(device_info.get("vpv2") or 0.0)
            ppv2 = float(device_info.get("ppv2") or 0.0)
            pv2_current = round(ppv2 / vpv2, 2) if vpv2 > 10.0 else 0.0

            vac1 = float(device_info.get("vac1") or 0.0)
            p_grid = abs(float(device_info.get("pactogridtotal") or 0.0))
            grid_current = round(p_grid / vac1, 2) if vac1 > 50.0 else 0.0

            eps_power = float(device_info.get("epsPower") or 0.0)
            v_eps = vac1 if vac1 > 50.0 else 230.0
            eps_current = round(eps_power / v_eps, 2)
            eps_apparent_power = round(eps_power * 1.05, 1)

            # 2. Moving Averages
            pv_total = float(device_info.get("pvPower") or device_info.get("ppvAll") or 0.0)
            pcharge = float(device_info.get("pcharge") or 0.0)
            pdischarge = float(device_info.get("pdischarge") or 0.0)
            net_battery_power = pcharge - pdischarge
            load_power = float(device_info.get("loadPower") or device_info.get("plocalLoadtotal") or 0.0)
            grid_signed = float(device_info.get("pactogridtotal") or 0.0)

            self.pv_history.append(pv_total)
            self.battery_history.append(net_battery_power)
            self.grid_history.append(grid_signed)
            self.eps_history.append(eps_power)
            self.load_history.append(load_power)

            avg_pv = round(sum(self.pv_history) / len(self.pv_history), 1) if self.pv_history else pv_total
            avg_bat = round(sum(self.battery_history) / len(self.battery_history), 1) if self.battery_history else net_battery_power
            avg_grid = round(sum(self.grid_history) / len(self.grid_history), 1) if self.grid_history else grid_signed
            avg_eps = round(sum(self.eps_history) / len(self.eps_history), 1) if self.eps_history else eps_power
            avg_load = round(sum(self.load_history) / len(self.load_history), 1) if self.load_history else load_power

            # 3. SOC Speed & Power Speed
            soc = float(device_info.get("soc") or 0.0)
            if self.last_soc is not None and self.last_soc_time is not None:
                dt_h = (now - self.last_soc_time).total_seconds() / 3600.0
                if dt_h >= (10.0 / 3600.0):  # update speed if >= 10s elapsed
                    self.soc_speed = round((soc - self.last_soc) / dt_h, 2)
                    if self.last_battery_power is not None:
                        self.power_speed = round((net_battery_power - self.last_battery_power) / dt_h, 1)
                    self.last_soc = soc
                    self.last_soc_time = now
                    self.last_battery_power = net_battery_power
            else:
                self.last_soc = soc
                self.last_soc_time = now
                self.last_battery_power = net_battery_power

            # 4. Battery Charge ETA
            inv_data = detailed_info.get("invData", {})
            capacity_ah = float(inv_data.get("bmSGaugeFCC") or 100.0)
            vbat = float(device_info.get("vbat") or inv_data.get("vbat") or 51.2)
            if vbat < 30.0:
                vbat = 51.2

            eta_text = "Standby (Czuwanie)"
            if pcharge > 25.0 and soc < 99.5:
                total_wh = capacity_ah * vbat
                needed_wh = total_wh * ((100.0 - soc) / 100.0)
                hours_left = needed_wh / pcharge
                if hours_left < 24.0:
                    finish_time = now + datetime.timedelta(hours=hours_left)
                    eta_text = f"Pełna ok. {finish_time.strftime('%H:%M')} (za {int(hours_left)}h {int((hours_left % 1) * 60)}m)"
                else:
                    eta_text = "Ładowanie powolne (>24h)"
            elif pdischarge > 25.0 and soc > 4.0:
                total_wh = capacity_ah * vbat
                available_wh = total_wh * (soc / 100.0)
                hours_left = available_wh / pdischarge
                if hours_left < 48.0:
                    eta_text = f"Rozładowanie za {int(hours_left)}h {int((hours_left % 1) * 60)}m"
                else:
                    eta_text = "Rozładowanie powolne (>48h)"
            elif soc >= 99.5:
                eta_text = "Naładowana (100%)"

            calculated = {
                "pv1_current": pv1_current,
                "pv2_current": pv2_current,
                "grid_current": grid_current,
                "eps_current": eps_current,
                "eps_apparent_power": eps_apparent_power,
                "avg_pv_power": avg_pv,
                "avg_battery_power": avg_bat,
                "avg_grid_power": avg_grid,
                "avg_eps_load": avg_eps,
                "avg_house_load": avg_load,
                "battery_charge_eta": eta_text,
                "battery_soc_speed": self.soc_speed,
                "battery_power_speed": self.power_speed,
            }

            status_str = device_info.get("status2") or "Normal"
            self._add_log(
                f"Pobrano telemetrię: Status={status_str}, PV={pv_total}W, Dom={load_power}W, Bat={soc}% ({net_battery_power}W), Sieć={grid_signed}W"
            )

            return {
                "telemetry": device_info,
                "params": params_info,
                "details": detailed_info,
                "calculated": calculated,
            }
        except AohaiApiError as err:
            self._add_log(f"Błąd komunikacji z chmurą: {err}")
            raise UpdateFailed(f"Error communicating with Aohai API: {err}") from err

    async def async_set_parameter(self, key_value_list: list[str]) -> bool:
        """Send command to update inverter parameters and refresh local state."""
        self._add_log(f"Wysyłanie parametru do inwertera: {key_value_list}")
        success = await self.hass.async_add_executor_job(
            self.client.set_parameter, self.csn, self.dsn, self.addr, key_value_list
        )
        if success:
            self._add_log(f"Parametr przyjęty pomyślnie: {key_value_list}")
            await self.async_request_refresh()
        else:
            self._add_log(f"Falownik odrzucił parametr: {key_value_list}")
        return success
