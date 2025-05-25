from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, SessionDep
from app.models import Settlement, SettlementCreate, SettlementPublic

router = APIRouter(prefix="/settlements", tags=["settlements"])


def assert_current_user_involved(dto: SettlementCreate, current_user: CurrentUser):
    if current_user.id not in [dto.sending_party_id, dto.receiving_party_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create settlements for which you are the sending or receiving party.",
        )


@router.post("/", response_model=SettlementPublic)
def create(
    dto: SettlementCreate,
    current_user: CurrentUser,
    session: SessionDep,
):
    assert_current_user_involved(dto, current_user)
    settlement = Settlement.model_validate(
        dto,
        update={
            "owner_id": current_user.id,
        },
    )
    session.add(settlement)
    session.commit()
    session.refresh(settlement)
    return settlement
