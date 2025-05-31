from sqlmodel import Session, select

from app.models import User


def ensure_user_exists(*, session: Session, clerk_user_id: str) -> User:
    exists = session.exec(
        select(User).where(User.clerk_user_id == clerk_user_id)
    ).one_or_none()
    if exists:
        return exists
    db_obj = User.model_validate(
        None,
        update={
            "clerk_user_id": clerk_user_id,
        },
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj
