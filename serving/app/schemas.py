from pydantic import BaseModel, Field

class RecommendRequest(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    k: int = Field(default=10, ge=1, le=50)
    radius_m: int = Field(default=5000, ge=100, le=50000)
    user_id: str | None = None

class RecommendItem(BaseModel):
    id: str
    name: str
    cuisine: str
    distance_m: int
    score: float

class RecommendResponse(BaseModel):
    items: list[RecommendItem]
    strategy: str
    catalog_version: str
    model_version: str | None = None