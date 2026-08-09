from contextlib import asynccontextmanager
from serving.app.state import load_catalog
from serving.app.scoring import score_and_rank
from fastapi import FastAPI, HTTPException, Request, Response
from serving.app.schemas import RecommendRequest, RecommendItem, RecommendResponse
from serving.app.config import settings
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import numpy as np
import time
from serving.app.metrics import REQUEST_LATENCY, CATALOG_SIZE, CATALOG_INFO
_state = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _state
    _state = load_catalog(settings.catalog_path, settings.catalog_version)
    CATALOG_SIZE.set(len(_state.ids))
    CATALOG_INFO.labels(catalog_version=settings.catalog_version).set(1)
    yield
    _state = None


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def timing(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    strategy = getattr(request.state, "strategy", "none")
    REQUEST_LATENCY.labels(strategy=str(strategy), status=str(response.status_code), path=request.url.path).observe(elapsed)
    return response


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/readyz")
def readyz():
    st = _state
    if st is None:
        raise HTTPException(status_code=503, detail="catalog not loaded")
    return {"status": "ready", "catalog_version": st.osm_version, "n": st.n}


@app.post("/recommend", response_model=RecommendResponse)
async def recommend(req: RecommendRequest, request: Request):
    st = _state
    if st is None:
        raise HTTPException(status_code=503, detail="catalog not loaded")
    else:
        idx, scores, dists, strategy = score_and_rank(st, np.radians(req.lat), np.radians(req.lon), req.k, req.radius_m, w_pop=settings.w_pop, w_geo=settings.w_geo, tau_m=settings.tau_m)
        request.state.strategy = strategy
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