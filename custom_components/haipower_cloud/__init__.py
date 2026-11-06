"""The HaiPower Cloud / Sandisolar integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_DSN,
    CONF_CSN,
    CONF_DEVICE_NAME,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    CONF_ENTITY_MODE,
    ENTITY_MODE_FULL,
    ENTITY_MODE_BASIC,
)
from .api import AohaiApiClient
from .coordinator import AohaiDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.SELECT,
    Platform.NUMBER,
    Platform.BUTTON,
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HaiPower Cloud from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    dsn = entry.data[CONF_DSN]
    csn = entry.data.get(CONF_CSN, "")
    device_name = entry.data.get(CONF_DEVICE_NAME, entry.title or f"Inverter {dsn}")
    model_name = entry.data.get("model_name", "SD-PRO-EU 6.5K / AO-6KSL-G3")
    addr = entry.data.get("addr", 1)
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
    entity_mode = entry.options.get(CONF_ENTITY_MODE, entry.data.get(CONF_ENTITY_MODE, ENTITY_MODE_FULL))

    client = AohaiApiClient(username, password)

    # Initial login
    await hass.async_add_executor_job(client.login)

    coordinator = AohaiDataUpdateCoordinator(
        hass=hass,
        client=client,
        dsn=dsn,
        csn=csn,
        device_name=device_name,
        model_name=model_name,
        addr=addr,
        scan_interval=scan_interval,
        config_entry=entry,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward setups based on selected entity mode
    if entity_mode == ENTITY_MODE_BASIC:
        active_platforms = [Platform.SENSOR, Platform.SWITCH]
        _LOGGER.info("HaiPower Cloud loaded in BASIC mode (Basic sensors and Inverter Operation switch)")
    else:
        active_platforms = PLATFORMS
        _LOGGER.info("HaiPower Cloud loaded in FULL mode (All sensors and controls active)")

    await hass.config_entries.async_forward_entry_setups(entry, active_platforms)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update by reloading the config entry."""
    _LOGGER.info("HaiPower Cloud options updated, reloading config entry %s", entry.entry_id)
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
