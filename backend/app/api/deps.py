from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClientError
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from app.core.auth.oidc import verify_token
from app.core.repos.users_repo import UsersRepositoryDep
from app.models import User

bearer_auth_scheme = HTTPBearer()

TokenDep = Annotated[HTTPAuthorizationCredentials, Depends(bearer_auth_scheme)]


def get_current_user(users: UsersRepositoryDep, token: TokenDep) -> User:
    try:
        token_data = verify_token(token.credentials)
    except (InvalidTokenError, ValidationError, PyJWKClientError):
        # PyJWKClientError can occur if the JWKS endpoint is unreachable or the kid mentioned in the header was not found in the JWKS, e.g. if someone sends a JWT from a different issuer
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    user = users.find_one_by_clerk_user_id(token_data.sub)
    if not user:
        # we could not find the user, but we trust our Identity Provider
        # so we create a new user record
        created = users.create(
            clerk_user_id=token_data.sub,
        )
        return created
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


# TODO remove
def get_current_active_superuser(_current_user: CurrentUser) -> User:
    raise HTTPException(
        status_code=403, detail="The user doesn't have enough privileges"
    )
