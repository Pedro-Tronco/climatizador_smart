from datetime import datetime
from typing import Sequence, Optional

from fastapi import FastAPI

from .schemas import Occurrence
from .services import TelemetryService


class TelemetryController:
    def __init__(self, telemetry_service: TelemetryService) -> None:
        self._telemetry_service = telemetry_service

    def register_endpoints(self, app: FastAPI) -> None:
        @app.get("/api/occurrences", response_model=Sequence[Occurrence])
        def get_occurrences(
            timestamp: Optional[datetime] = None,
        ) -> Sequence[Occurrence]:
            return self._telemetry_service.get_readings(timestamp)
