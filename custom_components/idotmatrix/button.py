"""Button platform for iDotMatrix."""
from __future__ import annotations

import datetime
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import IDotMatrixEntity
from .client.modules.common import Common
from .client.modules.fullscreenColor import FullscreenColor

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the iDotMatrix buttons."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        IDotMatrixSyncTime(coordinator, entry),
        IDotMatrixClear(coordinator, entry),
    ])

class IDotMatrixSyncTime(IDotMatrixEntity, ButtonEntity):
    """Button to sync time."""

    _attr_icon = "mdi:clock-check"
    _attr_name = "Sync Time"

    @property
    def unique_id(self) -> str:
        return f"{self._mac}_sync_time"

    async def async_press(self) -> None:
        """Handle the button press."""
        # Use HA time or system time?
        # Ideally pass datetime.now() values
        # Common().setTime() currently doesn't take args, it uses system time.
        # Assuming system time of HA host is correct.
        await Common().setTime()

class IDotMatrixClear(IDotMatrixEntity, ButtonEntity):
    """Button to clear screen."""

    _attr_icon = "mdi:eraser"
    _attr_name = "Clear Screen"

    @property
    def unique_id(self) -> str:
        return f"{self._mac}_clear_screen"

    async def async_press(self) -> None:
        """Handle the button press."""
        # Set black screen
        await FullscreenColor().setMode(0, 0, 0)
