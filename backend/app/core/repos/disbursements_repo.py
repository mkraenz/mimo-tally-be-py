from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends
from pydantic import UUID4
from sqlalchemy import func
from sqlmodel import col, or_, select

from app.core.db import SessionDep
from app.models import Disbursement


class DisbursementsRepository:
    def __init__(self, session: SessionDep) -> None:
        self.session = session

    def create_and_refresh(self, disbursement: Disbursement) -> None:
        """
        Creates a new disbursement record in the database.
        WARNING: Refreshes the `disbursement` object in place with the new ID and other fields from the database.
        """
        self.session.add(disbursement)
        self.session.commit()
        self.session.refresh(disbursement)

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

    def find_all_between(
        self,
        first_user_id: UUID4,
        second_user_id: UUID4,
        limit: int,
        offset: int,
        exclude_settled: bool,
    ) -> Sequence[Disbursement]:
        get_all_between = (
            select(Disbursement)
            .where(col(Disbursement.deleted_at).is_(None))
            .where(
                or_(
                    Disbursement.paying_party_id == first_user_id
                    and Disbursement.on_behalf_of_party_id == second_user_id,
                    Disbursement.on_behalf_of_party_id == first_user_id
                    and Disbursement.paying_party_id == second_user_id,
                )
            )
            .offset(offset)
            .limit(limit)
        )
        if exclude_settled:
            get_all_between = get_all_between.where(
                col(Disbursement.settlement_id).is_(None)
            )
        return self.session.exec(get_all_between).all()

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
            .where(
                or_(
                    Disbursement.paying_party_id == receiving_party_id
                    and Disbursement.on_behalf_of_party_id == sending_party_id,
                    Disbursement.on_behalf_of_party_id == receiving_party_id
                    and Disbursement.paying_party_id == sending_party_id,
                )
            )
            .where(col(Disbursement.settlement_id).is_(None))  # i.e. not settled yet
        )
        return self.session.exec(find_affected_disbursements).all()


DisbursementRepositoryDep = Annotated[DisbursementsRepository, Depends()]
