from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.crud import ensure_user_exists


def test_get_users_normal_user_me(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    clerk_user_id = "user_2uYtK90rO3HFzRhvuAU8GVBZeqR"
    ensure_user_exists(session=db, clerk_user_id=clerk_user_id)

    r = client.get(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
