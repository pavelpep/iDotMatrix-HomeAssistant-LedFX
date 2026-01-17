"""LedFx Gateway for iDotMatrix - Receives WLED protocol data and displays on iDotMatrix."""
from __future__ import annotations

import asyncio
import logging
import io
import hashlib
import time
from typing import Optional, Callable, TYPE_CHECKING

from PIL import Image

if TYPE_CHECKING:
    from .coordinator import IDotMatrixCoordinator

_LOGGER = logging.getLogger(__name__)

# WLED Protocol Constants
WLED_DRGB = 2  # DRGB protocol (timeout, R, G, B, R, G, B, ...)
WLED_DRGBW = 3  # DRGBW protocol
WLED_DNRGB = 4  # DNRGB protocol (timeout, start_idx_high, start_idx_low, R, G, B, ...)


class LedFxGateway:
    """UDP Gateway that receives LedFx WLED protocol data and forwards to iDotMatrix display."""

    def __init__(
        self,
        coordinator: "IDotMatrixCoordinator",
        host: str = "0.0.0.0",
        port: int = 21324,
        screen_size: int = 32,
    ):
        """Initialize the LedFx Gateway.
        
        Args:
            coordinator: The IDotMatrixCoordinator instance
            host: Host to bind UDP server to
            port: Port to listen on (default 21324 for WLED)
            screen_size: Size of the display (16, 32, or 64)
        """
        self.coordinator = coordinator
        self.host = host
        self.port = port
        self.screen_size = screen_size
        
        self._server: Optional[asyncio.DatagramProtocol] = None
        self._transport: Optional[asyncio.DatagramTransport] = None
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
        # Frame buffer and optimization
        self._pixel_buffer = bytearray(screen_size * screen_size * 3)
        self._last_frame_hash: Optional[str] = None
        self._frame_count = 0
        self._last_fps_time = time.time()
        self._fps = 0.0
        
        # Rate limiting
        self._last_send_time = 0.0
        self._min_frame_interval = 0.033  # ~30 FPS max by default
        
        # Statistics
        self._frames_received = 0
        self._frames_sent = 0
        self._frames_skipped = 0

    @property
    def is_running(self) -> bool:
        """Return True if gateway is running."""
        return self._running

    @property
    def fps(self) -> float:
        """Return current FPS."""
        return self._fps

    @property
    def stats(self) -> dict:
        """Return gateway statistics."""
        return {
            "running": self._running,
            "fps": round(self._fps, 1),
            "frames_received": self._frames_received,
            "frames_sent": self._frames_sent,
            "frames_skipped": self._frames_skipped,
            "port": self.port,
        }

    def set_max_fps(self, max_fps: float) -> None:
        """Set maximum FPS (rate limiting)."""
        if max_fps > 0:
            self._min_frame_interval = 1.0 / max_fps
        else:
            self._min_frame_interval = 0.0

    async def start(self) -> bool:
        """Start the UDP gateway server."""
        if self._running:
            _LOGGER.warning("LedFx Gateway already running")
            return True

        try:
            loop = asyncio.get_running_loop()
            
            # Create UDP endpoint
            self._transport, self._server = await loop.create_datagram_endpoint(
                lambda: LedFxProtocol(self._on_data_received),
                local_addr=(self.host, self.port),
            )
            
            self._running = True
            self._last_fps_time = time.time()
            self._frame_count = 0
            
            _LOGGER.info(f"LedFx Gateway started on {self.host}:{self.port}")
            return True
            
        except Exception as e:
            _LOGGER.error(f"Failed to start LedFx Gateway: {e}")
            return False

    async def stop(self) -> None:
        """Stop the UDP gateway server."""
        if not self._running:
            return

        self._running = False
        
        if self._transport:
            self._transport.close()
            self._transport = None
            self._server = None

        _LOGGER.info("LedFx Gateway stopped")

    def _on_data_received(self, data: bytes) -> None:
        """Handle received UDP data (called from protocol)."""
        if not self._running:
            return
            
        self._frames_received += 1
        
        # Schedule async processing
        asyncio.create_task(self._process_frame(data))

    async def _process_frame(self, data: bytes) -> None:
        """Process received WLED protocol frame."""
        if len(data) < 2:
            return

        protocol = data[0]
        
        try:
            if protocol == WLED_DRGB:
                # DRGB: timeout, R, G, B, R, G, B, ...
                # timeout = data[1]  # Not used
                pixel_data = data[2:]
                await self._update_pixels_rgb(pixel_data)
                
            elif protocol == WLED_DNRGB:
                # DNRGB: timeout, start_high, start_low, R, G, B, ...
                # timeout = data[1]  # Not used
                start_idx = (data[2] << 8) | data[3]
                pixel_data = data[4:]
                await self._update_pixels_rgb(pixel_data, start_idx)
                
            elif protocol == WLED_DRGBW:
                # DRGBW: timeout, R, G, B, W, R, G, B, W, ...
                # timeout = data[1]  # Not used
                pixel_data = data[2:]
                await self._update_pixels_rgbw(pixel_data)
                
            else:
                _LOGGER.debug(f"Unknown WLED protocol: {protocol}")
                
        except Exception as e:
            _LOGGER.debug(f"Error processing frame: {e}")

    async def _update_pixels_rgb(self, pixel_data: bytes, start_idx: int = 0) -> None:
        """Update pixel buffer with RGB data."""
        num_pixels = len(pixel_data) // 3
        
        for i in range(num_pixels):
            pixel_idx = start_idx + i
            if pixel_idx >= self.screen_size * self.screen_size:
                break
                
            buffer_idx = pixel_idx * 3
            data_idx = i * 3
            
            self._pixel_buffer[buffer_idx] = pixel_data[data_idx]      # R
            self._pixel_buffer[buffer_idx + 1] = pixel_data[data_idx + 1]  # G
            self._pixel_buffer[buffer_idx + 2] = pixel_data[data_idx + 2]  # B

        await self._send_frame()

    async def _update_pixels_rgbw(self, pixel_data: bytes) -> None:
        """Update pixel buffer with RGBW data (ignoring W channel)."""
        num_pixels = len(pixel_data) // 4
        
        for i in range(num_pixels):
            if i >= self.screen_size * self.screen_size:
                break
                
            buffer_idx = i * 3
            data_idx = i * 4
            
            self._pixel_buffer[buffer_idx] = pixel_data[data_idx]      # R
            self._pixel_buffer[buffer_idx + 1] = pixel_data[data_idx + 1]  # G
            self._pixel_buffer[buffer_idx + 2] = pixel_data[data_idx + 2]  # B
            # W channel (data_idx + 3) is ignored

        await self._send_frame()

    async def _send_frame(self) -> None:
        """Send current frame to iDotMatrix display."""
        current_time = time.time()
        
        # Rate limiting
        if current_time - self._last_send_time < self._min_frame_interval:
            self._frames_skipped += 1
            return

        # Frame skip optimization - check if frame is identical
        frame_hash = hashlib.md5(self._pixel_buffer).hexdigest()
        if frame_hash == self._last_frame_hash:
            self._frames_skipped += 1
            return

        self._last_frame_hash = frame_hash
        self._last_send_time = current_time

        # Update FPS counter
        self._frame_count += 1
        elapsed = current_time - self._last_fps_time
        if elapsed >= 1.0:
            self._fps = self._frame_count / elapsed
            self._frame_count = 0
            self._last_fps_time = current_time
            _LOGGER.debug(f"LedFx Gateway FPS: {self._fps:.1f}")

        try:
            # Convert pixel buffer to image
            image = Image.frombytes(
                "RGB",
                (self.screen_size, self.screen_size),
                bytes(self._pixel_buffer),
            )

            # Compress to PNG with optimization
            png_buffer = io.BytesIO()
            image.save(png_buffer, format="PNG", optimize=True, compress_level=1)
            png_data = png_buffer.getvalue()

            # Send to display using the Image module
            from .client.modules.image import Image as IDMImage
            from .client.connectionManager import ConnectionManager
            
            # Ensure we're in DIY mode and send the image
            idm_image = IDMImage()
            
            # Create payloads from PNG data
            payloads = idm_image._createPayloads(png_data)
            
            conn = ConnectionManager()
            if conn:
                await conn.connect()
                await conn.send(data=payloads)
                self._frames_sent += 1
                
        except Exception as e:
            _LOGGER.debug(f"Error sending frame to display: {e}")


class LedFxProtocol(asyncio.DatagramProtocol):
    """UDP Protocol handler for LedFx data."""

    def __init__(self, callback: Callable[[bytes], None]):
        """Initialize the protocol.
        
        Args:
            callback: Function to call when data is received
        """
        self._callback = callback

    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        """Called when connection is established."""
        _LOGGER.debug("LedFx UDP connection established")

    def datagram_received(self, data: bytes, addr: tuple) -> None:
        """Called when UDP data is received."""
        self._callback(data)

    def error_received(self, exc: Exception) -> None:
        """Called when an error occurs."""
        _LOGGER.debug(f"LedFx UDP error: {exc}")

    def connection_lost(self, exc: Optional[Exception]) -> None:
        """Called when connection is lost."""
        if exc:
            _LOGGER.debug(f"LedFx UDP connection lost: {exc}")
