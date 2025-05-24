from enum import Enum
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.api.deps import SessionDep
from app.models import Disbursement

router = APIRouter(prefix="/disbursements", tags=["disbursements"])


class Currency(Enum):
    JPY = "JPY"
    EUR = "EUR"


class Money(BaseModel):
    amount: float = Field(
        ...,
        description="The amount paid in the specified currency.",
        examples=[1],
    )
    currency: Currency = Field(Currency.EUR)


class CreateDisbursementDto(BaseModel):
    payer_id: str
    paid_for_user_id: str
    comment: str | None = Field(max_length=512, default=None)
    paid_amount: Money


class GetDisbursementDto(BaseModel):
    id: UUID
    payer_id: str
    paid_for_user_id: str
    comment: str | None
    # created_at: datetime
    # updated_at: datetime
    paid_amount: Money


@router.post("/", response_model=GetDisbursementDto)
def create(dto: CreateDisbursementDto, session: SessionDep) -> GetDisbursementDto:
    # now = datetime.now(timezone.utc)
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
    result = GetDisbursementDto(
        **disbursement.model_dump(), paid_amount=Money(**disbursement.model_dump())
    )
    return result
