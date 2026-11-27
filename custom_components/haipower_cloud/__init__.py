"""The HaiPower Cloud / Sandisolar integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady

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
    PROFILE_AUTO,
    PROFILE_BASIC,
    PROFILE_READ_ONLY,
    get_effective_profile,
)
from .api import AohaiApiClient, AohaiApiError, AohaiAuthError
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
    model_name = entry.data.get("model_name", "Unknown")
    addr = entry.data.get("addr", 1)
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
    entity_mode = entry.options.get(CONF_ENTITY_MODE, entry.data.get(CONF_ENTITY_MODE, PROFILE_AUTO))

    client = AohaiApiClient(username, password)

    # Initial login
    try:
        await hass.async_add_executor_job(client.login)
    except AohaiAuthError as err:
        await hass.async_add_executor_job(client.close)
        raise ConfigEntryAuthFailed(f"Invalid HaiPower Cloud credentials: {err}") from err
    except AohaiApiError as err:
        await hass.async_add_executor_job(client.close)
        raise ConfigEntryNotReady(f"Unable to connect to HaiPower Cloud: {err}") from err

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

    # Forward setups based on selected entity mode / resolved model profile
    effective_profile = get_effective_profile(entity_mode, model_name)
    if effective_profile == PROFILE_BASIC:
        active_platforms = [Platform.SENSOR, Platform.SWITCH]
        _LOGGER.info("HaiPower Cloud loaded in BASIC mode (Basic sensors and Inverter Operation switch)")
    elif effective_profile == PROFILE_READ_ONLY:
        active_platforms = [Platform.SENSOR]
        _LOGGER.info("HaiPower Cloud loaded in READ-ONLY mode (sensors only) for model '%s'", model_name)
    else:
        active_platforms = PLATFORMS
        _LOGGER.info("HaiPower Cloud loaded with profile '%s' for model '%s'", effective_profile, model_name)

    coordinator.platforms = active_platforms
    await hass.config_entries.async_forward_entry_setups(entry, active_platforms)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update by reloading the config entry."""
    _LOGGER.info("HaiPower Cloud options updated, reloading config entry %s", entry.entry_id)
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator: AohaiDataUpdateCoordinator | None = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    platforms = coordinator.platforms if coordinator and coordinator.platforms else PLATFORMS
    unload_ok = await hass.config_entries.async_unload_platforms(entry, platforms)
    if unload_ok:
        removed = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        if removed is not None:
            await hass.async_add_executor_job(removed.client.close)

    return unload_ok
