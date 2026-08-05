#!/usr/bin/env python3
"""
Pull Edmonton food venues from OpenStreetMap via the Overpass API (no key).
Produces a faithful catalog CSV. Downstream concerns (popularity ordering,
feature vectors) live in serving/ and training/ on purpose.

Usage:
    python data/pull_osm.py
"""
import argparse, csv, sys, time
import requests

# Edmonton bounding box (S, W, N, E). A rectangle, not the legal city
# boundary, so it catches a little surrounding area. Fine for a
# synthetic-interaction portfolio; an admin-area lookup isn't worth it.
BBOX = (53.39, -113.71, 53.71, -113.30)

ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",  # fallback mirror
]

HEADERS = {
    "User-Agent": "edmonton-recsys/0.1 (portfolio project; deepak)"
}


KEEP_TAGS = ["name", "cuisine", "amenity", "takeaway",
             "outdoor_seating", "wheelchair", "website", "opening_hours"]

def build_query(bbox):
    s, w, n, e = bbox
    b = f"{s},{w},{n},{e}"
    parts = []
    for a in ("restaurant", "fast_food", "cafe"):
        parts.append(f'  node["amenity"="{a}"]({b});')
        parts.append(f'  way["amenity"="{a}"]({b});')
    body = "\n".join(parts)
    return f"[out:json][timeout:120];\n(\n{body}\n);\nout center tags;"

def fetch(query):
    for url in ENDPOINTS:
        for attempt in range(3):
            try:
                r = requests.post(url, data={"data": query}, headers=HEADERS, timeout=180)
                if r.status_code == 200:
                    return r.json()
                if r.status_code in (429, 504):  # rate-limited / busy
                    wait = 10 * (attempt + 1)
                    print(f"  {url} -> {r.status_code}, waiting {wait}s", file=sys.stderr)
                    time.sleep(wait); continue
                print(f"  {url} -> {r.status_code}", file=sys.stderr); break
            except requests.RequestException as ex:
                print(f"  {url} error: {ex}", file=sys.stderr); time.sleep(5)
    raise SystemExit("All Overpass endpoints failed. Try again in a few minutes.")

def element_to_row(el):
    tags = el.get("tags", {})
    if not tags.get("name"):
        return None  # can't recommend an unnamed venue
    lat = el.get("lat") or el.get("center", {}).get("lat")
    lon = el.get("lon") or el.get("center", {}).get("lon")
    if lat is None or lon is None:
        return None
    row = {"osm_type": el["type"], "osm_id": el["id"], "lat": lat, "lon": lon}
    for t in KEEP_TAGS:
        row[t] = tags.get(t, "")
    return row

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/edmonton_restaurants.csv")
    args = ap.parse_args()

    print("Querying Overpass ...", file=sys.stderr)
    data = fetch(build_query(BBOX))

    rows, dropped = [], 0
    for el in data.get("elements", []):
        row = element_to_row(el)
        rows.append(row) if row else (dropped := dropped + 1)

    # de-dupe: a venue can appear as both a node and a way
    seen, deduped = set(), []
    for r in rows:
        key = (r["name"], round(r["lat"], 5), round(r["lon"], 5))
        if key not in seen:
            seen.add(key); deduped.append(r)

    cols = ["osm_type", "osm_id", "lat", "lon"] + KEEP_TAGS
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader(); w.writerows(deduped)

    print(f"kept {len(deduped)} venues ({dropped} dropped, "
          f"{len(rows) - len(deduped)} dupes removed) -> {args.out}", file=sys.stderr)

if __name__ == "__main__":
    main()