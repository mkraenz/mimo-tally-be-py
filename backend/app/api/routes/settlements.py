import uuid
from functools import reduce

from fastapi import APIRouter, HTTPException, status
from pydantic import UUID4

from app.api.deps import CurrentUser
from app.api.http_exceptions import (
    not_found_exception,
    settlement_not_matching_amount_due,
    settlement_not_matching_disbursements_exception,
)
from app.core.db import SessionDep
from app.core.repos.disbursements_repo import DisbursementRepositoryDep
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
    # TODO currently only the sending party can create a settlement
    if current_user.id not in [dto.sending_party_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="For the time being, You can only create settlements for which you are the sending party, that is, the party paying some amount to the receiving party. The opposite direction is currently WIP.",
        )


@router.post("/", response_model=SettlementPublic, status_code=status.HTTP_201_CREATED)
def create(
    dto: SettlementCreate,
    current_user: CurrentUser,
    session: SessionDep,
    disbursements_repo: DisbursementRepositoryDep,
) -> Settlement:
    # TODO refactor
    # TODO sender and receiver can be identical
    assert_current_user_is_settling(dto, current_user)

    affected_disbursements = disbursements_repo.find_affected_for_settlement(
        settled_disbursement_ids=dto.settled_disbursement_ids,
        receiving_party_id=dto.receiving_party_id,
        sending_party_id=dto.sending_party_id,
    )

    # this simple check works thanks to uniqueness constraints in db and on the dto
    if not len(affected_disbursements) == len(dto.settled_disbursement_ids):
        raise settlement_not_matching_disbursements_exception()
    settlement = Settlement.model_validate(
        dto,
        update={
            "id": uuid.uuid4(),  # need id to update disbursements
            "owner_id": current_user.id,
        },
    )

    def to_total_amount_due(acc: float, d: Disbursement) -> float:
        if d.paying_party_id != dto.sending_party_id:
            return acc - d.amount
        return acc + d.amount

    # TODO we somehow need to get currencies in here, too.
    total = round(reduce(to_total_amount_due, affected_disbursements, 0.0), 2)
    print("Amount due:", total)
    if total != -dto.amount_paid:
        raise settlement_not_matching_amount_due()

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
