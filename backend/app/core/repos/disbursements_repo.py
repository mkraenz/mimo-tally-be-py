from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends
from pydantic import UUID4
from sqlalchemy import func
from sqlmodel import col, select

from app.core.db import SessionDep
from app.models import Disbursement


class DisbursementsRepository:
    def __init__(self, session: SessionDep) -> None:
        self.session = session

    def find_one_owned(self, id: UUID4, owner_id: UUID4) -> Disbursement | None:
        statement = (
            select(Disbursement)
            .where(Disbursement.id == id)
            .where(Disbursement.owner_id == owner_id)
            .where(col(Disbursement.deleted_at).is_(None))
        )
        return self.session.exec(statement).one_or_none()

    def find_all_owned(
        self, owner_id: UUID4, limit: int, offset: int
    ) -> Sequence[Disbursement]:
        get_all = (
            select(Disbursement)
            .where(Disbursement.owner_id == owner_id)
            .offset(offset)
            .limit(limit)
        )
        return self.session.exec(get_all).all()

    def count_owned(self, owner_id: UUID4) -> int:
        statement = (
            select(func.count())
            .select_from(Disbursement)
            .where(Disbursement.owner_id == owner_id)
        )
        return self.session.exec(statement).one()

    def soft_delete(self, disbursement: Disbursement) -> None:
        disbursement.sqlmodel_update({"deleted_at": datetime.now(timezone.utc)})
        self.session.add(disbursement)
        self.session.commit()

    def find_affected_for_settlement(
        self,
        settled_disbursement_ids: list[str],
        receiving_party_id: UUID4,
        sending_party_id: UUID4,
    ) -> Sequence[Disbursement]:
        find_affected_disbursements = (
            select(Disbursement)
            .where(col(Disbursement.id).in_(settled_disbursement_ids))
            .where(col(Disbursement.deleted_at).is_(None))
            .where(Disbursement.payer_id == receiving_party_id)
            .where(Disbursement.paid_for_user_id == sending_party_id)
            .where(col(Disbursement.settlement_id).is_(None))  # i.e. not settled yet
        )
        return self.session.exec(find_affected_disbursements).all()


DisbursementRepositoryDep = Annotated[DisbursementsRepository, Depends()]
