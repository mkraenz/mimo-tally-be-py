from typing import Annotated

from fastapi import APIRouter, Query, status
from pydantic import UUID4

from app.api.deps import CurrentUser
from app.api.http_exceptions import not_found_exception
from app.core.repos.disbursements_repo import DisbursementRepositoryDep
from app.models import (
    Disbursement,
    DisbursementCreate,
    DisbursementPublic,
    DisbursementsPublic,
    Money,
)

router = APIRouter(prefix="/disbursements", tags=["disbursements"])


@router.post("/", response_model=DisbursementPublic)
def create(
    dto: DisbursementCreate, repo: DisbursementRepositoryDep, current_user: CurrentUser
) -> DisbursementPublic:
    disbursement = Disbursement.model_validate(
        dto,
        update={
            "amount": dto.amount_paid.amount,
            "currency": dto.amount_paid.currency.value,
            "owner_id": current_user.id,
        },
    )
    repo.create_and_refresh(disbursement)
    return DisbursementPublic(
        **disbursement.model_dump(), amount_paid=Money(**disbursement.model_dump())
    )


@router.get("/")
def find_all(
    current_user: CurrentUser,
    repo: DisbursementRepositoryDep,
    limit: Annotated[int, Query(max=100)] = 10,
    offset: Annotated[int, Query(min=0)] = 0,
) -> DisbursementsPublic:
    disbursements = repo.find_all_owned(current_user.id, limit, offset)
    data = list(map(DisbursementPublic.make, disbursements))
    total = repo.count_owned(current_user.id)
    return DisbursementsPublic(data=data, total=total)


@router.get("/{id}")
def find_one(
    id: UUID4, current_user: CurrentUser, repo: DisbursementRepositoryDep
) -> DisbursementPublic:
    disbursement = repo.find_one_owned(id, current_user.id)
    if not disbursement:
        raise not_found_exception()
    return DisbursementPublic.make(disbursement)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Soft-deletes the given resource.",
)
def delete(
    id: UUID4, current_user: CurrentUser, repo: DisbursementRepositoryDep
) -> None:
    disbursement = repo.find_one_owned(id, owner_id=current_user.id)
    if not disbursement:
        raise not_found_exception()
    repo.soft_delete(disbursement)
