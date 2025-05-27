from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.crud import create_user_new


def test_create_disbursement(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    clerk_user_id = "user_2uYtK90rO3HFzRhvuAU8GVBZeqR"
    user = create_user_new(session=db, clerk_user_id=clerk_user_id)

    data = {
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
    # assert response.status_code == 201
    content = response.json()
    assert content["amount_paid"] == data["amount_paid"]
    assert content["comment"] == data["comment"]
    assert content["on_behalf_of_party_id"] == data["on_behalf_of_party_id"]
    assert content["paying_party_id"] == data["paying_party_id"]
    assert "id" in content
    # TODO add prop
    # assert "owner_id" in content
    assert "updated_at" in content
    assert "created_at" in content
