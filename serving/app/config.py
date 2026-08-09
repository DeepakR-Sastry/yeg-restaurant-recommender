from pydantic_settings import BaseSettings

LATENCY_BUCKETS = (
    0.0003, 0.0004, 0.0005, 0.0006, 0.0008,
    0.001, 0.0015, 0.002, 0.003, 0.005,
    0.010, 0.025, 0.050, 0.100, 0.250, 0.500,
)

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