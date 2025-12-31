"""Switch platform for iDotMatrix."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import EntityCategory

from .const import DOMAIN
from .entity import IDotMatrixEntity

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the iDotMatrix switch platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        IDotMatrixTextProportional(coordinator, entry),
        IDotMatrixMultiline(coordinator, entry),
        IDotMatrixAutosize(coordinator, entry),
        IDotMatrixClockDate(coordinator, entry),
    ])

class IDotMatrixAutosize(IDotMatrixEntity, SwitchEntity):
    """Switch to toggle automatic font sizing (Perfect Fit)."""

    _attr_icon = "mdi:arrow-expand-all"
    _attr_name = "Text Perfect Fit (Autosize)"
    _attr_entity_category = EntityCategory.CONFIG
    
    @property
    def unique_id(self) -> str:
        return f"{self._mac}_text_autosize"

    @property
    def is_on(self) -> bool:
        return self.coordinator.text_settings.get("autosize", False)

    async def async_turn_on(self, **kwargs) -> None:
        self.coordinator.text_settings["autosize"] = True
        # If multiline is not on, maybe we should turn it on? 
        # Autosize implies fitting text to screen, which usually requires wrapping.
        # But let's respect the user's explicit multiline choice or assume autosize enforces a fit strategy.
        # For now, just setting the flag. The coordinator will use it.
        # Ideally, Perfect Fit should probably imply Multiline mode or at least standard text scaling.
        # Let's force multiline ON if Autosize is turned ON, as autosizing single line scroller is less common/useful?
        # User said "resize text perfectly to the screen", usually means static display. Scrollers don't need resizing to fit.
        if not self.coordinator.text_settings.get("multiline"):
             self.coordinator.text_settings["multiline"] = True
             
        await self.coordinator.async_update_device()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self.coordinator.text_settings["autosize"] = False
        await self.coordinator.async_update_device()
        self.async_write_ha_state()

class IDotMatrixClockDate(IDotMatrixEntity, SwitchEntity):
    """Switch to toggle date on clock."""

    _attr_icon = "mdi:calendar"
    _attr_name = "Clock Show Date"
    _attr_entity_category = EntityCategory.CONFIG
    
    @property
    def unique_id(self) -> str:
        return f"{self._mac}_clock_date"

    @property
    def is_on(self) -> bool:
        return self.coordinator.text_settings.get("clock_date", True)

    async def async_turn_on(self, **kwargs) -> None:
        self.coordinator.text_settings["clock_date"] = True
        # Update clock immediately
        s = self.coordinator.text_settings
        color = s.get("color", [255, 255, 255])
        style = s.get("clock_style", 0)
        h24 = s.get("clock_format", "24h") == "24h"
        
        from .client.modules.clock import Clock
        await Clock().setMode(style, True, h24, color[0], color[1], color[2])
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self.coordinator.text_settings["clock_date"] = False
        # Update clock immediately
        s = self.coordinator.text_settings
        color = s.get("color", [255, 255, 255])
        style = s.get("clock_style", 0)
        h24 = s.get("clock_format", "24h") == "24h"
        
        from .client.modules.clock import Clock
        await Clock().setMode(style, False, h24, color[0], color[1], color[2])
        self.async_write_ha_state()

class IDotMatrixTextProportional(IDotMatrixEntity, SwitchEntity):
    """Switch to toggle proportional text rendering."""

    _attr_icon = "mdi:format-text-variant"
    _attr_name = "Proportional Spacing"
    _attr_entity_category = EntityCategory.CONFIG
    
    @property
    def unique_id(self) -> str:
        return f"{self._mac}_text_proportional"

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self.coordinator.text_settings.get("proportional", True)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        self.coordinator.text_settings["proportional"] = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        self.coordinator.text_settings["proportional"] = False
        self.async_write_ha_state()

class IDotMatrixMultiline(IDotMatrixEntity, SwitchEntity):
    """Switch to toggle multiline text (static image)."""

    _attr_icon = "mdi:wrap"
    _attr_name = "Multiline Text"
    _attr_entity_category = EntityCategory.CONFIG
    
    @property
    def unique_id(self) -> str:
        return f"{self._mac}_text_multiline"

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self.coordinator.text_settings.get("multiline", False)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        self.coordinator.text_settings["multiline"] = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        self.coordinator.text_settings["multiline"] = False
        self.async_write_ha_state()
