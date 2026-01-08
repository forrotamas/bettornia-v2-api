from pydantic import BaseModel
import os

def env_flag(name: str, default: str = "0") -> bool:
    return os.getenv(name, default) == "1"

def env_int(name: str, default: str) -> int:
    return int(os.getenv(name, default))

class Settings(BaseModel):
    # Hard kill-switch: if true, live actions are forbidden globally.
    no_live: bool = env_flag("NO_LIVE", "1")

    # Capability gates (rollout controls)
    enable_shadow_submit: bool = env_flag("ENABLE_SHADOW_SUBMIT", "1")
    enable_live_submit: bool = env_flag("ENABLE_LIVE_SUBMIT", "0")

    # Second factor arming token (must be provided via header)
    live_arm_token: str = os.getenv("LIVE_ARM_TOKEN", "")

    # Abuse guards
    max_body_bytes: int = env_int("MAX_BODY_BYTES", "65536")  # 64 KiB
    replay_ttl_seconds: int = env_int("REPLAY_TTL_SECONDS", "300")  # 5 min

    # Rate limits per minute (per source IP)
    rl_shadow_per_min: int = env_int("RL_SHADOW_PER_MIN", "60")
    rl_live_per_min: int = env_int("RL_LIVE_PER_MIN", "6")
    rl_settlement_per_min: int = env_int("RL_SETTLEMENT_PER_MIN", "30")
    rl_reconcile_per_min: int = env_int("RL_RECONCILE_PER_MIN", "10")

    database_url: str = os.getenv("DATABASE_URL", "")

settings = Settings()
