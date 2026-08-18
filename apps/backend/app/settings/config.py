from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env", extra = "ignore")

    
    DATABASE_URL : str
    FRONTEND_URL : str
    CLERK_SECRET_KEY : str
    CLERK_JWKS_URL : str
    CLERK_WEBHOOK_SECRET : str


settings = Settings()

