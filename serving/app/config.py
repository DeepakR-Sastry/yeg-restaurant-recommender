from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    catalog_path: str = "data/edmonton_restaurants.csv"
    catalog_version: str = "osm-2026-08-07"

    w_pop: float = 0.5
    w_geo: float = 0.5
    tau_m: float = 1500.0

    default_k: int = 10
    default_radius_m: int = 5000

    class Config:
        env_prefix = "YEG_"


settings = Settings()