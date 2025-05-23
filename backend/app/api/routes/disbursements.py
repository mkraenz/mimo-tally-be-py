from datetime import datetime
from enum import Enum
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.api.deps import SessionDep
from app.models import Disbursement

router = APIRouter(prefix="/disbursements", tags=["disbursements"])


class Currency(Enum):
    JPY = "JPY"
    EUR_CENT = "EUR Cent"


class Money(BaseModel):
    amount: int = Field(..., description="The amount paid in the specified currency")
    currency: Currency


class CreateDisbursementDto(BaseModel):
    payer_id: str
    paid_for_user_id: str
    comment: str | None = Field(max_length=512, default=None)
    amount: Money


class GetDisbursementDto(BaseModel):
    id: UUID
    payer_id: str
    paid_for_user_id: str
    comment: str | None
    created_at: datetime
    updated_at: datetime
    amount: Money


@router.post("/", response_model=GetDisbursementDto)
def create(dto: CreateDisbursementDto, _session: SessionDep):
    # now = datetime.now(timezone.utc)
    return Disbursement(
        paid_for_user_id=dto.paid_for_user_id,
        payer_id=dto.payer_id,
        amount=dto.amount.amount,
        currency=dto.amount.currency.value,
        comment=dto.comment,
        # created_at=now,
        # updated_at=now,
    )
