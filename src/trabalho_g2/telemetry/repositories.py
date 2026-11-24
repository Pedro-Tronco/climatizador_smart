from typing import Sequence
from datetime import datetime

from ..database import engine

from sqlmodel import (
    Session, 
    select,
)

from .schemas import (
    Occurrence,
)


class TelemetryRepository:
    def __init__(self) -> None:
        self._engine = engine


    def get_all_occurrences(self) -> Sequence[Occurrence]:
        with Session(self._engine) as session:
            statement = select(Occurrence)
            result = session.exec(statement)
            return result.all()
        
        
    def get_occurrences_since_timestamp(self, timestamp: datetime) -> Sequence[Occurrence]:
        with Session(self._engine) as session:
                statement = select(Occurrence).where(Occurrence.timestamp > timestamp)
                result = session.exec(statement)
                return result.all()
            
            
    def write_occurance(self, occurrance: Occurrence) -> Occurrence:
        with Session(self._engine) as session:
            session.add(occurrance)
            session.commit()
            session.refresh(occurrance)
            return occurrance