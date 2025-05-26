from typing import Annotated

from fastapi import Depends
from sqlmodel import select

from app.core.db import SessionDep
from app.models import User


class UsersRepository:
    def __init__(self, session: SessionDep) -> None:
        self.session = session

    def find_one_by_clerk_user_id(self, clerk_user_id: str) -> User | None:
        find_user_by_clerk_uid = select(User).where(User.clerk_user_id == clerk_user_id)
        return self.session.exec(find_user_by_clerk_uid).one_or_none()


UsersRepositoryDep = Annotated[UsersRepository, Depends()]
