"""Sensor platform for iDotMatrix."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import IDotMatrixEntity

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the iDotMatrix sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        IDotMatrixLedFxFpsSensor(coordinator, entry),
    ])


class IDotMatrixLedFxFpsSensor(IDotMatrixEntity, SensorEntity):
    """Sensor showing LedFx Gateway current FPS."""

    _attr_icon = "mdi:gauge"
    _attr_name = "LedFx Gateway FPS"
    _attr_native_unit_of_measurement = "FPS"
    _attr_state_class = SensorStateClass.MEASUREMENT
    # No entity_category - appears as main sensor on device page
    
    @property
    def unique_id(self) -> str:
        return f"{self._mac}_ledfx_fps"

    @property
    def native_value(self) -> float | None:
        """Return the current FPS."""
        stats = self.coordinator.ledfx_stats
        return round(stats.get("fps", 0), 1)

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        stats = self.coordinator.ledfx_stats
        return {
            "running": stats.get("running", False),
            "frames_received": stats.get("frames_received", 0),
            "frames_sent": stats.get("frames_sent", 0),
            "frames_skipped": stats.get("frames_skipped", 0),
            "port": stats.get("port", 21324),
        }

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True
