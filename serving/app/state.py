from dataclasses import dataclass
import pandas as pd
import numpy as np

@dataclass(frozen=True)
class CatalogState:
    osm_version: str
    n: int

    lat_rad: np.ndarray
    lon_rad: np.ndarray
    pop: np.ndarray

    ids: list[str]
    names: list[str]
    cuisines: list[str]

PRIOR_TAGS = ["cuisine", "takeaway", "outdoor_seating", "wheelchair", "website", "opening_hours"]

def load_catalog(csv_path: str, osm_version: str) -> CatalogState:
    df = pd.read_csv(csv_path)
    df = df[df["name"].notna() & (df["name"].str.strip() != "")]

    ids = (df["osm_type"] + "/" + df["osm_id"].astype(str)).tolist()
    names = df["name"].tolist()
    cuisines = df["cuisine"].fillna("").tolist()

    lat_rad = np.radians(df["lat"].to_numpy(dtype=np.float32))
    lon_rad = np.radians(df["lon"].to_numpy(dtype=np.float32))

    pop_prior = df[PRIOR_TAGS].notna()
    pop_prior = (pop_prior.sum(axis=1)/len(PRIOR_TAGS)).to_numpy(dtype=np.float32)
    n = len(ids)
    if n == 0:
        raise ValueError("No restaurants found!")
    state = CatalogState(osm_version=osm_version, n=n, lat_rad=lat_rad, lon_rad=lon_rad, pop=pop_prior, ids=ids, names=names, cuisines=cuisines)

    return state

if __name__ == "__main__":
    load_catalog("../../data/edmonton_restaurants.csv", 1)
