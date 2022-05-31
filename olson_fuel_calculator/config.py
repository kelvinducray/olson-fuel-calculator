from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    DEFAULT_PRE_FIRE_FUEL_LOAD: float = 20.2  # Positive value
    DEFAULT_DECAY_CONST: float = 0.35  # Between 0 & 1
    DEFAULT_FUEL_REMAINING: float = 0.5  # Between 0 & 1
    DEFAULT_YEARS_SINCE_FIRE: int = 5  # Positive value


@lru_cache
def get_settings():
    return Settings()
