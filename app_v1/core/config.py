from pydantic_settings import BaseSettings
from pydantic import BaseModel
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent


class DbSettings(BaseModel):
    url: str = "postgresql+asyncpg://user:886688zsewdc@localhost:5432/resume_database"
    echo: bool = False


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt_private_key.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt_public_key.pem"
    algorithm: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    RESPONSE_TOKEN_EXPIRE_DAYS: int = 7


class Settings(BaseSettings):
    api_v1_prefix: str = '/api/v1'
    alembic_prefix: str = '/alembic'
    db: DbSettings = DbSettings()
    auth_JWT: AuthJWT = AuthJWT()


settings = Settings()
