from dataclasses import dataclass
from enum import StrEnum
from sqlmodel import SQLModel, Field
from datetime import datetime

from ..arduino.schemas import LedColors
from ..settings import get_timezone


def _local_now() -> datetime:
    return datetime.now(get_timezone())


class SensorState(StrEnum):
    INITIALIZING = LedColors.WHITE
    OK = LedColors.GREEN
    WARNING = LedColors.BLUE
    DISABLED = LedColors.RED

@dataclass
class StatusMessage:
    current_status: str

    def __post_init__(self):
        if self.current_status not in SensorState.__members__:
            valid_names = ", ".join(SensorState.__members__.keys())
            raise ValueError(f"Invalid status '{self.current_status}'. Expected one of: {valid_names}")


class Occurrence(SQLModel, table=True):
    timestamp: datetime = Field(default_factory=_local_now, primary_key=True)
    type: str = Field(index=True)
