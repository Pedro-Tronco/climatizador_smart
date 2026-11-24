from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATABASE_PATH = DATA_DIR / "database.db"

engine = create_engine(
    f"sqlite:///{DATABASE_PATH}",
    connect_args={"check_same_thread": False},
)


def initialize_database() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
