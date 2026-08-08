import numpy as np
from serving.app.state import load_catalog
EARTH_RADIUS_M = 6371000.0

def haversine_m(lat1: float, lon1: float, lat2: np.ndarray, lon2: np.ndarray):
    a = (np.sin((lat2-lat1)/2)) ** 2 + np.cos(lat1) * np.cos(lat2) * (np.sin((lon2-lon1)/2)) ** 2
    d = 2 * EARTH_RADIUS_M * np.arcsin(np.sqrt(a))
    return d

def score_and_rank(st, user_lat_rad, user_lon_rad, k, radius_m, w_pop=0.5, w_geo=0.5, tau_m = 1500.0):
    distances_to_venues = haversine_m(user_lat_rad, user_lon_rad, st.lat_rad, st.lon_rad)

    mask = distances_to_venues <= radius_m
    if mask.sum() == 0:
        strategy = "popularity_global"
        sort_indices = np.argpartition(st.pop, -k)[-k:]
        idx = sort_indices[np.argsort(st.pop[sort_indices])[::-1]]
        scores = st.pop[idx]
        return (idx, scores, distances_to_venues[idx], strategy)
    else:
        strategy = "popularity_geo"
        idx = np.flatnonzero(mask)
        cand_d = distances_to_venues[idx]
        scores = st.pop[idx]

        cand_scores = w_pop * scores + w_geo * np.exp(-cand_d / tau_m)

        kk = min(k, len(idx))
        top = np.argpartition(cand_scores, -kk)[-kk:]
        top = top[np.argsort(cand_scores[top])[::-1]]

        return_idx = idx[top]
        return return_idx, cand_scores[top], cand_d[top], strategy

if __name__ == "__main__":
    state = load_catalog("../../data/edmonton_restaurants.csv", 1)
    idx, scores, distances, strategy = score_and_rank(
    state, np.radians(53.5461), np.radians(-113.4938), 5, 1000
)
    for i, s, d in zip(idx, scores, distances):
        print(f"{state.names[i]:35s} score={s:.3f} d={d:6.0f}m")

