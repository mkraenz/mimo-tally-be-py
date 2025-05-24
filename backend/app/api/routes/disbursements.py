from fastapi import APIRouter

from app.api.deps import SessionDep
from app.models import Disbursement, DisbursementPublic, Money

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
    result = DisbursementPublic(
        **disbursement.model_dump(), paid_amount=Money(**disbursement.model_dump())
    )
    return result
