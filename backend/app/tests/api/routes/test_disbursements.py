from typing import Any

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.crud import ensure_user_exists


def test_create_disbursement(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    clerk_user_id = "user_2uYtK90rO3HFzRhvuAU8GVBZeqR"
    user = ensure_user_exists(session=db, clerk_user_id=clerk_user_id)

    data: dict[str, Any] = {
        "amount_paid": {"amount": 10.50, "currency": "EUR"},
        "comment": "food",
        "on_behalf_of_party_id": str(user.id),
        "paying_party_id": str(user.id),
    }
    response = client.post(
        f"{settings.API_V1_STR}/disbursements/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["amount_paid"] == data["amount_paid"]
    assert body["comment"] == data["comment"]
    assert body["on_behalf_of_party_id"] == data["on_behalf_of_party_id"]
    assert body["paying_party_id"] == data["paying_party_id"]
    assert "id" in body
    assert "owner_id" in body
    assert "updated_at" in body
    assert "created_at" in body
