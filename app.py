"""ATS Resume Scorer — Flask web app.

Paste a resume and a job description, get a visual match report.
Run it locally with:

    pip install -r requirements.txt
    python app.py

then open http://127.0.0.1:5000
"""

import os

from flask import Flask, jsonify, render_template, request

from scorer import analyze

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")


def _load_sample(name):
    with open(os.path.join(SAMPLES_DIR, f"{name}.txt"), encoding="utf-8") as f:
        return f.read()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/samples/<name>")
def sample(name):
    if name not in ("sample_resume", "sample_job_description"):
        return jsonify({"error": "unknown sample"}), 404
    return jsonify({"text": _load_sample(name)})


@app.route("/analyze", methods=["POST"])
def analyze_page():
    resume = request.form.get("resume_text", "")
    jd = request.form.get("jd_text", "")
    if not resume.strip() or not jd.strip():
        return render_template(
            "index.html",
            error="Paste both a resume and a job description first.",
            resume_text=resume,
            jd_text=jd,
        )
    return render_template(
        "report.html", result=analyze(resume, jd),
        resume_text=resume, jd_text=jd,
    )


@app.route("/api/analyze", methods=["POST"])
def analyze_api():
    payload = request.get_json(force=True, silent=True) or {}
    return jsonify(analyze(payload.get("resume", ""), payload.get("job_description", "")))


if __name__ == "__main__":
    app.run(debug=True)
