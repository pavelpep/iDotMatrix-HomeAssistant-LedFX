"""DataUpdateCoordinator for iDotMatrix."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN
from .client.connectionManager import ConnectionManager

_LOGGER = logging.getLogger(__name__)


class IDotMatrixCoordinator(DataUpdateCoordinator):
    """Class to manage fetching iDotMatrix data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60),
        )
        self.entry = entry

    async def _async_update_data(self):
        """Fetch data from the device."""
        # For now, we don't really 'fetch' much state from the device as it's write-heavy.
        # But we could check connection status.
        return {"connected": True}
