"""
Unit Tests for FastAPI Backend Endpoints
SIH26168 - Smart Vehicles | Indian Space Research Organisation (ISRO)
"""

from fastapi.testclient import TestClient
import pytest

from backend.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "IntelliDR"
    assert data["problem_statement"] == "SIH26168"
    assert data["theme"] == "Smart Vehicles"
    assert data["organization"] == "Indian Space Research Organisation (ISRO)"


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "subsystems" in data


def test_models_endpoint():
    response = client.get("/models")
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        data = response.json()
        assert data["model_name"] == "IntelliDR-Velocity-Net"
        assert "sha256_checksum" in data


def test_benchmarks_endpoint():
    response = client.get("/benchmarks")
    assert response.status_code == 200
    data = response.json()
    assert "sih_drift_requirement" in data or "drift_metrics" in data


def test_system_endpoint():
    response = client.get("/system")
    assert response.status_code == 200
    data = response.json()
    assert data["problem_statement"] == "SIH26168"
    assert "pipeline_stages" in data
