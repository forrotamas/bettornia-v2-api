from pydantic import BaseModel
import os

class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL", "")
    no_live: bool = os.getenv("NO_LIVE", "1") == "1"

settings = Settings()
