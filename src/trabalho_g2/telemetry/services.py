from datetime import datetime
from typing import Optional, Sequence

from ..arduino.schemas import SensorReading, LedColors
from ..arduino.controller import ArduinoController
from ..settings import get_timezone

from .websockets import TelemetryWebsocket
from .repositories import TelemetryRepository

from .schemas import (
    StatusMessage,
    SensorState,
    Occurrence,
)


class TelemetryService:
    def __init__(
        self,
        arduino_controller: ArduinoController,
        telemetry_websocket: TelemetryWebsocket,
        telemetry_repository: TelemetryRepository,
    ) -> None:
        self._arduino_controller = arduino_controller
        self._telemetry_websocket = telemetry_websocket
        self._telemetry_repository = telemetry_repository

        self._state: SensorState = SensorState.INITIALIZING


    def _update_sensor_state(self, reading: SensorReading) -> None:
        if reading.sensor1 and reading.sensor2:
            self._state = SensorState.OK

        elif not reading.sensor1 and not reading.sensor2:
            self._state = SensorState.DISABLED

        else:
            self._state = SensorState.WARNING

    def handle_sensor_reading(self, reading: SensorReading) -> None:
        self._update_sensor_state(reading)

        self._telemetry_repository.write_occurance(Occurrence(
            type=self._state.name,
        ))

        self._arduino_controller.set_led_color(LedColors(self._state.value))

        self._telemetry_websocket.send_message(StatusMessage(
            current_status=self._state.name
        ))

    def get_readings(self, start_timestamp: Optional[datetime]) -> Sequence[Occurrence]:
        if start_timestamp is not None and start_timestamp.utcoffset() is None:
            start_timestamp = start_timestamp.replace(tzinfo=get_timezone())

        return (
            self._telemetry_repository.get_all_occurrences()
            if start_timestamp is None
            else self._telemetry_repository.get_occurrences_since_timestamp(start_timestamp)
        )
