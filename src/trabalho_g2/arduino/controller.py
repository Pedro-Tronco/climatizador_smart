from typing import Callable
from pydantic import ValidationError
import serial
import threading
import time

from .schemas import (
    LedColors,
    SensorReading,
)


class ArduinoController:

    def __init__(
        self,
        port: str,
        baudrate: int = 115200
    ):

        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=0.5,
            write_timeout=1
        )

        time.sleep(2)

        self.serial.reset_input_buffer()

        self._stop_event = threading.Event()
        self._reader_thread = None
        self._write_lock = threading.Lock()

        self._last_isolated: SensorReading | None = None


    def set_led_color(self, color: LedColors) -> None:
        with self._write_lock:
            self.serial.write(color.value.encode("ascii"))


    def _process_sensor_data(self, line, toggle_callback) -> None:
        try:
            reading = SensorReading.model_validate(line)
        except ValidationError:
            return

        if reading != self._last_isolated:

            self._last_isolated = reading
            toggle_callback(reading)
            

    def _read_loop(
        self,
        toggle_callback: Callable[[SensorReading], None]
    ) -> None:

        while not self._stop_event.is_set():

            try:
                raw_line = self.serial.readline()

            except serial.SerialException as error:
                print(f"Serial communication error: {error}")
                self._stop_event.set()
                break

            if not raw_line:
                continue

            line = raw_line.decode(
                "ascii",
                errors="replace"
            ).strip()

            self._process_sensor_data(
                line,
                toggle_callback
            )

    def start(
        self,
        toggle_callback: Callable[[SensorReading], None]
    ):

        if self._reader_thread and self._reader_thread.is_alive():
            raise RuntimeError("Arduino listener is already running")

        self._stop_event.clear()

        self._reader_thread = threading.Thread(
            target=self._read_loop,
            args=(toggle_callback,),
            daemon=True
        )

        self._reader_thread.start()

    def close(self):

        self._stop_event.set()

        if self._reader_thread:
            self._reader_thread.join(timeout=1)

        if self.serial.is_open:
            self.serial.close()
