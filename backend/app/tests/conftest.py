from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.config import Settings
from app.core.db import engine, init_db
from app.main import app
from app.models import User


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        statement = delete(User)
        session.execute(statement)
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


# TODO rename. not a token of the superuser
@pytest.fixture(scope="module")
def superuser_token_headers() -> dict[str, str]:
    token = Settings.TEST_JWT
    headers = {"Authorization": f"Bearer {token}"}
    return headers
