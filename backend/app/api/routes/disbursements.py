from typing import Annotated

from fastapi import APIRouter, Query, status
from pydantic import UUID4
from sqlalchemy import func
from sqlmodel import select

from app.api.deps import SessionDep
from app.api.routes.disbursements_repo import DisbursementRepositoryDep
from app.api.routes.http_exceptions import not_found_exception
from app.models import (
    Disbursement,
    DisbursementCreate,
    DisbursementPublic,
    DisbursementsPublic,
    Money,
)

router = APIRouter(prefix="/disbursements", tags=["disbursements"])


@router.post("/", response_model=DisbursementPublic)
def create(dto: DisbursementCreate, session: SessionDep) -> DisbursementPublic:
    disbursement = Disbursement.model_validate(
        dto,
        update={
            "amount": dto.amount_paid.amount,
            "currency": dto.amount_paid.currency.value,
        },
    )
    session.add(disbursement)
    session.commit()
    session.refresh(disbursement)
    return DisbursementPublic(
        **disbursement.model_dump(), amount_paid=Money(**disbursement.model_dump())
    )


def count(session: SessionDep) -> int:
    statement = select(func.count()).select_from(Disbursement)
    return session.exec(statement).one()


@router.get("/")
def find_all(
    session: SessionDep,
    limit: Annotated[int, Query(max=100)] = 10,
    offset: Annotated[int, Query(min=0)] = 0,
) -> DisbursementsPublic:
    get_all = select(Disbursement).offset(offset).limit(limit)
    disbursements = session.exec(get_all).all()

    data = list(map(DisbursementPublic.make, disbursements))
    total = count(session)
    return DisbursementsPublic(data=data, total=total)


@router.get("/{id}")
def find_one(id: UUID4, repo: DisbursementRepositoryDep) -> DisbursementPublic:
    disbursement = repo.find_one(id)
    if not disbursement:
        raise not_found_exception()
    return DisbursementPublic.make(disbursement)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Soft-deletes the given resource.",
)
def delete(id: UUID4, repo: DisbursementRepositoryDep) -> None:
    disbursement = repo.find_one(id)
    if not disbursement:
        raise not_found_exception()
    repo.soft_delete(disbursement)
