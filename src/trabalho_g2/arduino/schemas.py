from enum import StrEnum
from pydantic import BaseModel, model_validator


class SensorReading(BaseModel):

    sensor1: bool
    sensor2: bool

    @model_validator(mode="before")
    @classmethod
    def parse_serial_output(cls, data):

        if isinstance(data, str):

            parts = data.strip().split(",")

            if len(parts) != 3 or parts[0] != "OBJECT":
                raise ValueError("Invalid sensor output")

            if parts[1] not in ("0", "1") or parts[2] not in ("0", "1"):
                raise ValueError("Invalid sensor values")

            return {
                "sensor1": parts[1] == "1",
                "sensor2": parts[2] == "1"
            }

        return data

    @property
    def isolated(self) -> bool:
        return self.sensor1 and self.sensor2


class LedColors(StrEnum):
    RED = "LED,RED\n"
    GREEN = "LED,GREEN\n"
    BLUE = "LED,BLUE\n"
    YELLOW = "LED,YELLOW\n"
    CYAN = "LED,CYAN\n"
    MAGENTA = "LED,MAGENTA\n"
    WHITE = "LED,WHITE\n"
    OFF = "LED,OFF\n"