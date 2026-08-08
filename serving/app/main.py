from contextlib import asynccontextmanager
from serving.app.state import load_catalog
from serving.app.scoring import score_and_rank
from fastapi import FastAPI, HTTPException
from serving.app.schemas import RecommendRequest, RecommendItem, RecommendResponse
from serving.app.config import settings
import numpy as np
import time

_state = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _state
    _state = load_catalog(settings.catalog_path, settings.catalog_version)
    yield
    _state = None


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def timing(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    # TODO: print elapsed (in ms) and response.status_code
    return response


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    st = _state
    if st is None:
        raise HTTPException(status_code=503, detail="catalog not loaded")
    return {"status": "ready", "catalog_version": st.osm_version, "n": st.n}


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    st = _state
    if st is None:
        raise HTTPException(status_code=503, detail="catalog not loaded")
    else:
        idx, scores, dists, strategy = score_and_rank(st, np.radians(req.lat), np.radians(req.lon), req.k, req.radius_m, w_pop=settings.w_pop, w_geo=settings.w_geo, tau_m=settings.tau_m)
        items = [
        RecommendItem(
            id=st.ids[i],
            name=st.names[i],
            cuisine=st.cuisines[i],
            distance_m=int(d),
            score=float(s),
        )
        for i, s, d in zip(idx, scores, dists)
    ]


        

    return RecommendResponse(items=items, strategy=strategy, catalog_version=st.osm_version)