import random
import string

from app.core.config import settings


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def get_superuser_token_headers() -> dict[str, str]:
    token = settings.TEST_JWT
    headers = {"Authorization": f"Bearer {token}"}
    return headers
