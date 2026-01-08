from pydantic import BaseModel
import os

def env_flag(name: str, default: str = "0") -> bool:
    return os.getenv(name, default) == "1"

class Settings(BaseModel):
    # Hard kill-switch: if true, live actions are forbidden globally.
    no_live: bool = env_flag("NO_LIVE", "1")

    # Capability gates (rollout controls)
    enable_shadow_submit: bool = env_flag("ENABLE_SHADOW_SUBMIT", "1")
    enable_live_submit: bool = env_flag("ENABLE_LIVE_SUBMIT", "0")

    # Second factor arming token (must be provided via header)
    live_arm_token: str = os.getenv("LIVE_ARM_TOKEN", "")

    database_url: str = os.getenv("DATABASE_URL", "")

settings = Settings()
