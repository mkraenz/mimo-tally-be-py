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

    def create(
        self, *, clerk_user_id: str, is_active: bool = True, is_superuser: bool = False
    ) -> User:
        user = User(
            clerk_user_id=clerk_user_id,
            is_active=is_active,
            is_superuser=is_superuser,
            # TODO this wont work for more than one user bc of uniqueness of emails
            email="a@b.com",
            hashed_password="hashed_password",
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user


UsersRepositoryDep = Annotated[UsersRepository, Depends()]
