from ..arduino.schemas import SensorReading, LedColors
from ..arduino.controller import ArduinoController

from .websockets import TelemetryWebsocket

from .schemas import (
    StatusMessage,
    SensorState,
)


class TelemetryService:
    def __init__(
        self,
        arduino_controller: ArduinoController,
        telemetry_websocket: TelemetryWebsocket
    ) -> None:
        self._arduino_controller = arduino_controller
        self._telemetry_websocket = telemetry_websocket
        
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
        
        self._arduino_controller.set_led_color(LedColors(self._state.value))
        
        self._telemetry_websocket.send_message(StatusMessage(
            current_status=self._state.name
        ))
        
        