from fastapi.testclient import TestClient
import serving.app.main as main
from serving.app.schemas import RecommendItem

def test_healthz_ok():
    client = TestClient(main.app)
    response = client.get("/healthz")
    assert response.status_code == 200

def test_cold_start_not_ready():
    main._state = None
    client = TestClient(main.app)
    response = client.get("/healthz")
    assert response.status_code == 200
    response = client.get("/readyz")
    assert response.status_code == 503

def test_empty_radius_degrades():
    with TestClient(main.app) as client:
        response = client.post("/recommend", json={"lat": 0, "lon": 0, "k": 3, "radius_m": 100
        })
        assert response.json()["strategy"] == "popularity_global"
        assert response.status_code != 500
        print(response.status_code, response.text)

def test_response_schema_stable():
    with TestClient(main.app) as client:
        response = client.post("/recommend", json={"lat": 53.5444, "lon": -113.4909, "k": 3, "radius_m": 1000
        })
        assert response.status_code == 200
        body = response.json()
        assert "strategy" in body
        assert "catalog_version" in body
        assert "model_version" in body
        assert isinstance(body["items"], list)
        assert len(body["items"]) <= 3


        assert len(body["items"]) > 0
        for item in body["items"]:
            assert isinstance(item["id"], str)
            assert isinstance(item["name"], str)
            assert isinstance(item["cuisine"], str)
            assert isinstance(item["distance_m"], int)
            assert isinstance(item["score"], float)