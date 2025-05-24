from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import func
from sqlmodel import select

from app.api.deps import SessionDep
from app.models import Disbursement, DisbursementPublic, DisbursementsPublic, Money

router = APIRouter(prefix="/disbursements", tags=["disbursements"])


@router.post("/", response_model=DisbursementPublic)
def create(dto: DisbursementPublic, session: SessionDep) -> DisbursementPublic:
    disbursement = Disbursement.model_validate(
        dto,
        update={
            "amount": dto.paid_amount.amount,
            "currency": dto.paid_amount.currency.value,
        },
    )
    session.add(disbursement)
    session.commit()
    session.refresh(disbursement)
    return DisbursementPublic(
        **disbursement.model_dump(), paid_amount=Money(**disbursement.model_dump())
    )


def count(session: SessionDep):
    statement = select(func.count()).select_from(Disbursement)
    return session.exec(statement).one()


@router.get("/", response_model=DisbursementsPublic)
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
