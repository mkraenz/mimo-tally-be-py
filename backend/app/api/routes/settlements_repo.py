from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends
from pydantic import UUID4
from sqlalchemy import func
from sqlmodel import col, select

from app.api.deps import SessionDep
from app.models import Settlement


class SettlementsRepository:
    def __init__(self, session: SessionDep) -> None:
        self.session = session

    def find_one(self, id: UUID4) -> Settlement | None:
        statement = (
            select(Settlement)
            .where(Settlement.id == id)
            .where(col(Settlement.deleted_at).is_(None))
        )
        return self.session.exec(statement).one_or_none()

    def soft_delete(self, settlement: Settlement) -> None:
        settlement.sqlmodel_update({"deleted_at": datetime.now(timezone.utc)})
        self.session.add(settlement)
        self.session.commit()

    def find_one_owned(self, id: UUID4, owner_id: UUID4) -> Settlement | None:
        statement = (
            select(Settlement)
            .where(col(Settlement.deleted_at).is_(None))
            .where(Settlement.owner_id == owner_id)
            .where(Settlement.id == id)
        )
        return self.session.exec(statement).one_or_none()

    def find_all_owned(self, owner_id: UUID4) -> Sequence[Settlement]:
        statement = (
            select(Settlement)
            .where(col(Settlement.deleted_at).is_(None))
            .where(Settlement.owner_id == owner_id)
        )
        return self.session.exec(statement).all()

    def count_owned(self, owner_id: UUID4) -> int:
        statement = (
            select(func.count())
            .select_from(Settlement)
            .where(Settlement.owner_id == owner_id)
        )
        return self.session.exec(statement).one()


SettlementsRepositoryDep = Annotated[SettlementsRepository, Depends()]
