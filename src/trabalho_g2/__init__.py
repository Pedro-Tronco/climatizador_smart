import asyncio

from fastapi import FastAPI

from .settings import get_settings
from .registry import get_services
from .database import initialize_database
from .arduino.schemas import LedColors


app = FastAPI()


def main() -> None:
    asyncio.run(_run())


async def _run() -> None:
    import uvicorn

    initialize_database()
    settings = get_settings()
    services = get_services(settings)

    try:
        services.telemetry_controller.register_endpoints(app)
        services.telemetry_websocket.start()
        services.arduino_controller.start(
            toggle_callback=services.telemetry_service.handle_sensor_reading
        )

        server = uvicorn.Server(
            uvicorn.Config(app, host="0.0.0.0", port=8000)
        )
        await server.serve()
    finally:
        services.arduino_controller.set_led_color(LedColors.OFF)
        services.arduino_controller.close()
        services.telemetry_websocket.stop()
