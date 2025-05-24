from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends
from pydantic import UUID4
from sqlmodel import select

from app.api.deps import SessionDep
from app.models import Disbursement


class DisbursementsRepository:
    def __init__(self, session: SessionDep) -> None:
        self.session = session

    def find_one(self, id: UUID4) -> Disbursement | None:
        statement = (
            select(Disbursement)
            .where(Disbursement.id == id)
            .where(
                # https://github.com/fastapi/sqlmodel/issues/109#issuecomment-2585072083
                Disbursement.deleted_at == None  # noqa E711 Comparison to `None` should be `cond is None`.
            )
        )
        return self.session.exec(statement).one_or_none()

    def soft_delete(self, disbursement: Disbursement):
        disbursement.sqlmodel_update({"deleted_at": datetime.now(timezone.utc)})
        self.session.add(disbursement)
        self.session.commit()


DisbursementRepositoryDep = Annotated[DisbursementsRepository, Depends()]
