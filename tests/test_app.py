from app import app

def test_home_endpoint():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert response.json["status"] == "running"
    assert response.json["version"] == "1.0.0"


def test_health_endpoint():
    client = app.test_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_ready_endpoint():
    client = app.test_client()
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json["status"] == "ready"


def test_metrics_endpoint():
    client = app.test_client()
    client.get("/health")
    response = client.get("/metrics")
    output = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "flask_http_requests_total" in output
    assert "flask_http_request_duration_seconds_count" in output
