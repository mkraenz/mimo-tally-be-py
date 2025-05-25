from fastapi import APIRouter

from app.api.deps import SessionDep

router = APIRouter(prefix="/settlements", tags=["settlements"])


@router.post("")
def create(_session: SessionDep):
    pass
