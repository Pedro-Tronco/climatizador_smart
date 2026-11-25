from dataclasses import dataclass

from .settings import Settings

from .arduino.controller import ArduinoController

from .raspi.controller import RaspiController

from .telemetry.routes import TelemetryController
from .telemetry.repositories import TelemetryRepository
from .telemetry.websockets import TelemetryWebsocket
from .telemetry.services import TelemetryService

from .air_conditioner.services import AirConditionerService
from .air_conditioner.routes import AirConditionerController


@dataclass
class ServiceContainer:
    arduino_controller: ArduinoController
    raspi_controller: RaspiController
    telemetry_websocket: TelemetryWebsocket
    telemetry_service: TelemetryService
    telemetry_controller: TelemetryController
    
    ac_service: AirConditionerService
    ac_controller: AirConditionerController


def get_services(settings: Settings) -> ServiceContainer:
    arduino = ArduinoController(port=settings.arduino_port)
    
    raspi = RaspiController()

    ac_service = AirConditionerService(raspi)
    ac_controller = AirConditionerController(ac_service)

    telemetry_websocket = TelemetryWebsocket()
    telemetry_repository = TelemetryRepository()
    telemetry_service = TelemetryService(
        arduino_controller=arduino,
        telemetry_websocket=telemetry_websocket,
        telemetry_repository=telemetry_repository,
        ac_service=ac_service,
    )
    telemetry_controller = TelemetryController(telemetry_service)

    return ServiceContainer(
        arduino_controller=arduino,
        raspi_controller=raspi,
        telemetry_websocket=telemetry_websocket,
        telemetry_service=telemetry_service,
        telemetry_controller=telemetry_controller,
        ac_service=ac_service,
        ac_controller=ac_controller,
    )
