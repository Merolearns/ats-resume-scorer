import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # noqa: E402


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_index_loads(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"ATS Resume Scorer" in r.data


def test_sample_endpoints(client):
    for name in ("sample_resume", "sample_job_description"):
        r = client.get(f"/samples/{name}")
        assert r.status_code == 200
        assert len(r.get_json()["text"]) > 100


def test_sample_unknown_404(client):
    assert client.get("/samples/nope").status_code == 404


def test_analyze_requires_both_inputs(client):
    r = client.post("/analyze", data={"resume_text": "x", "jd_text": ""})
    assert r.status_code == 200
    assert b"Paste both" in r.data


def test_analyze_renders_report(client):
    r = client.post(
        "/analyze",
        data={
            "resume_text": "SUMMARY\nPython analyst.\nEXPERIENCE\nUsed Python and SQL.\nEDUCATION\nBS.",
            "jd_text": "Need Python, SQL and Airflow.",
        },
    )
    assert r.status_code == 200
    assert b"Matched skills" in r.data
    assert b"airflow" in r.data.lower()


def test_api_analyze_json(client):
    r = client.post(
        "/api/analyze",
        json={"resume": "Python and SQL.", "job_description": "Need Python, SQL."},
    )
    assert r.status_code == 200
    data = r.get_json()
    assert data["score"] >= 0
    assert "matched_skills" in data
    assert "tips" in data
