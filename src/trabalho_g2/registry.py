from dataclasses import dataclass
from .settings import Settings
from .arduino.controller import ArduinoController
from .telemetry.websockets import TelemetryWebsocket
from .telemetry.services import TelemetryService


@dataclass
class ServiceContainer:
    arduino_controller: ArduinoController
    telemetry_websocket: TelemetryWebsocket
    telemetry_service: TelemetryService


def get_services(settings: Settings) -> ServiceContainer:
    arduino = ArduinoController(port=settings.arduino_port)

    telemetry_websocket = TelemetryWebsocket()
    telemetry_service = TelemetryService(
        arduino_controller=arduino,
        telemetry_websocket=telemetry_websocket,
    )

    return ServiceContainer(
        arduino_controller=arduino,
        telemetry_websocket=telemetry_websocket,
        telemetry_service=telemetry_service,
    )