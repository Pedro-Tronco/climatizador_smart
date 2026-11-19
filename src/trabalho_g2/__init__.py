from .settings import get_settings
from .registry import get_services
from .arduino.schemas import LedColors
from tornado.ioloop import IOLoop


def main() -> None:
    settings = get_settings()
    services = get_services(settings)
    io_loop = IOLoop.current()

    try:
        services.telemetry_websocket.start()
        services.arduino_controller.start(
            toggle_callback=services.telemetry_service.handle_sensor_reading
        )
        io_loop.start()
    finally:
        services.arduino_controller.set_led_color(LedColors.OFF)
        services.arduino_controller.close()
        services.telemetry_websocket.stop()
