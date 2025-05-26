import uuid
from functools import reduce

from fastapi import APIRouter, HTTPException, status
from pydantic import UUID4
from sqlmodel import col, select

from app.api.deps import CurrentUser
from app.api.routes.http_exceptions import not_found_exception
from app.core.db import SessionDep
from app.core.repos.settlements_repo import SettlementsRepositoryDep
from app.models import (
    Disbursement,
    Settlement,
    SettlementCreate,
    SettlementPublic,
    SettlementsPublic,
)

router = APIRouter(prefix="/settlements", tags=["settlements"])


def assert_current_user_is_settling(
    dto: SettlementCreate, current_user: CurrentUser
) -> None:
    # TODO implement that
    # if current_user.id not in [dto.sending_party_id, dto.receiving_party_id]:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="You can only create settlements for which you are the sending or receiving party.",
    #     )
    if current_user.id not in [dto.sending_party_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="For the time being, You can only create settlements for which you are the sending party, that is, the party paying some amount to the receiving party. The opposite direction is currently WIP.",
        )


@router.post("/", response_model=SettlementPublic)
def create(
    dto: SettlementCreate,
    current_user: CurrentUser,
    session: SessionDep,
) -> Settlement:
    # TODO refactor
    # TODO sender and receiver can be identical
    assert_current_user_is_settling(dto, current_user)
    find_affected_disbursements = (
        select(Disbursement)
        .where(col(Disbursement.id).in_(dto.settled_disbursement_ids))
        .where(col(Disbursement.deleted_at).is_(None))
        .where(Disbursement.payer_id == dto.receiving_party_id)
        .where(Disbursement.paid_for_user_id == dto.sending_party_id)
        .where(col(Disbursement.settlement_id).is_(None))  # i.e. not settled yet
    )
    affected_disbursements = session.exec(find_affected_disbursements).all()
    # this simple check works thanks to uniqueness constraints in db and on the dto
    if not len(affected_disbursements) == len(dto.settled_disbursement_ids):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Some or all disbursements listed in settled_disbursement_ids have not been found or are otherwise do not refer correctly to payer or paid parties of some of those disbursements. Make sure that you are the receiving party for every disbursement listed in settled_disbursement_ids (i.e. somebody paid for you).",
        )
    settlement = Settlement.model_validate(
        dto,
        update={
            "id": uuid.uuid4(),  # need id to update disbursements
            "owner_id": current_user.id,
        },
    )

    # TODO we somehow need to get currencies in here, too.
    total = reduce(lambda acc, d: acc + d.amount, affected_disbursements, 0.0)
    if total != dto.amount_paid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The amount due of all affected disbursements does not match the amount provided in the request body.",
        )

    for disbursement in affected_disbursements:
        disbursement.sqlmodel_update({"settlement_id": settlement.id})
    session.add(settlement)
    session.add_all(affected_disbursements)
    session.commit()
    session.refresh(settlement)
    return settlement


@router.get("/")
def find_all_owned(
    current_user: CurrentUser, repo: SettlementsRepositoryDep
) -> SettlementsPublic:
    settlements = repo.find_all_owned(current_user.id)
    total = repo.count_owned(current_user.id)
    settlements_mapped = list(map(SettlementPublic.make, settlements))
    return SettlementsPublic(data=settlements_mapped, total=total)


@router.get("/{id}", response_model=SettlementPublic)
def find_one(
    id: UUID4, current_user: CurrentUser, repo: SettlementsRepositoryDep
) -> Settlement:
    settlement = repo.find_one_owned(id, owner_id=current_user.id)
    if not settlement:
        raise not_found_exception()
    return settlement
