"""
IntelliDR External IMU & Sensor Stream Adapter
SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
Team: Logic Legend2 (Team ID: 170889)

Provides universal ingestion for external industrial, vehicular, and FOG IMUs:
- Network streaming via UDP socket listener
- Serial interface adapter (RS-232 / USB COM port)
- Supported formats: CSV strings, JSON packets, binary 6-axis / 9-axis frames
- Configurable scale factors (e.g. g to m/s^2, deg/s to rad/s) and axis remapping
"""

import json
import socket
import struct
import time
from typing import Callable, Optional
import numpy as np

from intellidr_core.sensor_types import IMUSample


class ExternalIMUAdapter:
    """Universal external IMU parser and protocol decoder."""

    def __init__(
        self,
        accel_scale: float = 1.0,      # Default: inputs in m/s^2. If inputs in g, scale=9.80665
        gyro_scale: float = 1.0,       # Default: inputs in rad/s. If inputs in deg/s, scale=pi/180
        axis_mapping: str = "XYZ",     # Re-order axes if sensor has different hardware orientation
    ):
        self.accel_scale = accel_scale
        self.gyro_scale = gyro_scale
        self.axis_mapping = axis_mapping.upper()

    def parse_csv_line(self, line: str) -> Optional[IMUSample]:
        """
        Parse CSV line:
        timestamp, ax, ay, az, gx, gy, gz, [mx, my, mz]
        """
        parts = [p.strip() for p in line.strip().split(",")]
        if len(parts) < 7:
            return None

        try:
            ts = float(parts[0])
            ax = float(parts[1]) * self.accel_scale
            ay = float(parts[2]) * self.accel_scale
            az = float(parts[3]) * self.accel_scale
            gx = float(parts[4]) * self.gyro_scale
            gy = float(parts[5]) * self.gyro_scale
            gz = float(parts[6]) * self.gyro_scale

            mx = float(parts[7]) if len(parts) > 7 else None
            my = float(parts[8]) if len(parts) > 8 else None
            mz = float(parts[9]) if len(parts) > 9 else None

            return IMUSample(
                timestamp=ts,
                ax=ax, ay=ay, az=az,
                gx=gx, gy=gy, gz=gz,
                mx=mx, my=my, mz=mz
            )
        except (ValueError, IndexError):
            return None

    def parse_json_packet(self, data_str: str) -> Optional[IMUSample]:
        """Parse JSON packet: {"ts": ..., "ax": ..., "ay": ..., "az": ..., "gx": ..., "gy": ..., "gz": ...}"""
        try:
            d = json.loads(data_str)
            return IMUSample(
                timestamp=float(d.get("ts", d.get("timestamp", time.time()))),
                ax=float(d.get("ax", 0.0)) * self.accel_scale,
                ay=float(d.get("ay", 0.0)) * self.accel_scale,
                az=float(d.get("az", 0.0)) * self.accel_scale,
                gx=float(d.get("gx", 0.0)) * self.gyro_scale,
                gy=float(d.get("gy", 0.0)) * self.gyro_scale,
                gz=float(d.get("gz", 0.0)) * self.gyro_scale,
                mx=float(d["mx"]) if "mx" in d else None,
                my=float(d["my"]) if "my" in d else None,
                mz=float(d["mz"]) if "mz" in d else None,
            )
        except Exception:
            return None

    def parse_binary_frame(self, data: bytes) -> Optional[IMUSample]:
        """
        Parse packed binary frame:
        Header (0xAA, 0x55) + double timestamp (8B) + 6 x float32 (24B) = 34 bytes
        """
        if len(data) < 34:
            return None
        if data[0] != 0xAA or data[1] != 0x55:
            return None

        try:
            ts, ax, ay, az, gx, gy, gz = struct.unpack(">d6f", data[2:34])
            return IMUSample(
                timestamp=ts,
                ax=ax * self.accel_scale,
                ay=ay * self.accel_scale,
                az=az * self.accel_scale,
                gx=gx * self.gyro_scale,
                gy=gy * self.gyro_scale,
                gz=gz * self.gyro_scale,
            )
        except struct.error:
            return None


class ExternalIMUSocketServer:
    """Asynchronous UDP stream receiver for external IMUs."""

    def __init__(self, host: str = "0.0.0.0", port: int = 5555, adapter: Optional[ExternalIMUAdapter] = None):
        self.host = host
        self.port = port
        self.adapter = adapter or ExternalIMUAdapter()
        self.is_running = False

    def listen(self, callback: Callable[[IMUSample], None], max_packets: Optional[int] = None):
        """Bind socket and stream incoming packets to callback."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.settimeout(2.0)
        self.is_running = True

        count = 0
        try:
            while self.is_running:
                try:
                    data, addr = sock.recvfrom(2048)
                except socket.timeout:
                    continue

                sample = None
                if data.startswith(b"\xAA\x55"):
                    sample = self.adapter.parse_binary_frame(data)
                else:
                    text = data.decode("utf-8", errors="ignore").strip()
                    if text.startswith("{"):
                        sample = self.adapter.parse_json_packet(text)
                    else:
                        sample = self.adapter.parse_csv_line(text)

                if sample is not None:
                    callback(sample)
                    count += 1
                    if max_packets is not None and count >= max_packets:
                        break
        finally:
            sock.close()
            self.is_running = False
