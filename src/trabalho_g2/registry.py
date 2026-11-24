from dataclasses import dataclass
from .settings import Settings
from .arduino.controller import ArduinoController
from .telemetry.controller import TelemetryController
from .telemetry.repositories import TelemetryRepository
from .telemetry.websockets import TelemetryWebsocket
from .telemetry.services import TelemetryService


@dataclass
class ServiceContainer:
    arduino_controller: ArduinoController
    telemetry_websocket: TelemetryWebsocket
    telemetry_service: TelemetryService
    telemetry_controller: TelemetryController


def get_services(settings: Settings) -> ServiceContainer:
    arduino = ArduinoController(port=settings.arduino_port)

    telemetry_websocket = TelemetryWebsocket()
    telemetry_repository = TelemetryRepository()
    telemetry_service = TelemetryService(
        arduino_controller=arduino,
        telemetry_websocket=telemetry_websocket,
        telemetry_repository=telemetry_repository,
    )
    telemetry_controller = TelemetryController(telemetry_service)

    return ServiceContainer(
        arduino_controller=arduino,
        telemetry_websocket=telemetry_websocket,
        telemetry_service=telemetry_service,
        telemetry_controller=telemetry_controller,
    )
