import jwt
from pydantic import BaseModel

from app.core.config import settings

jwks_url = f"https://{settings.CLERK_DOMAIN}/.well-known/jwks.json"
# audience = settings.CLERK_AUDIENCE
issuer = settings.CLERK_ISSUER
algorithm = "RS256"


class JwtBody(BaseModel):
    azp: str
    exp: int
    fva: list[int]
    iat: int
    iss: str
    nbf: int
    sid: str
    sub: str


def verify_token(access_token: str) -> JwtBody:
    header = jwt.get_unverified_header(access_token)
    jwks_client = jwt.PyJWKClient(jwks_url)
    key = jwks_client.get_signing_key(header["kid"]).key
    decoded = jwt.decode(
        access_token,
        key,
        [algorithm],
        issuer=issuer,
        options={"verify_exp": not settings.INSECURE_SKIP_JWT_EXPIRATION_CHECK},
    )
    return JwtBody.model_validate(decoded)


if __name__ == "__main__":
    jwt_body = verify_token(
        # expired token
        "eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18ydVgzODdKWWx6bm9KSldobnE4d21qYlRPV1QiLCJ0eXAiOiJKV1QifQ.eyJhenAiOiJodHRwczovL3RhbGx5LmtyYWVuei5ldSIsImV4cCI6MTc0ODI1NDcxNiwiZnZhIjpbMjQsLTFdLCJpYXQiOjE3NDgyNTQ2NTYsImlzcyI6Imh0dHBzOi8vY2xlcmsudGFsbHkua3JhZW56LmV1IiwibmJmIjoxNzQ4MjU0NjQ2LCJzaWQiOiJzZXNzXzJ4ZDFZU1JNVWp3WGJWVlVvWVhJaXVIV3ptcyIsInN1YiI6InVzZXJfMnVZdEs5MHJPM0hGelJodnVBVThHVkJaZXFSIn0.XvAjgJ6QFcbdbw80cgDH95Y0e-oJL-tXrsNIIzudqra3e1SgBa-FuWLwlp5QRIykb23bHuq3THbJyF_5byDRS1rujTVnRvB7mUynBkyvmvx3Zh9siw5x5rWOz9u5JcS7dKvPdD4OWtFXCeRAP0VbMgx4B4NDLt98ZYjl5kf7bGI_-eBsVIXHP3ro1GOPvH7T2laPKbuOjdocpz1bDRUjjTa3tJSaC6nAWgYDc0SaySjmorAdBFeqpGHWYrrob3khDc5UDtNZL7A0kpqdO4hbe_nzQS9HBlGdQib06CY_qy_K13rExwFnbNz69jlsIqn_MLAq8fBhhUFWTerXHvnozA"
    )
    print(jwt_body)
