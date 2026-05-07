"""Flask API and optional template interface for AI Resume Analyzer."""

from __future__ import annotations

import tempfile
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from analyzer import analyze_resume, save_report_json
from utils import read_resume_file


app = Flask(__name__)
CORS(app)


@app.after_request
def add_no_cache_headers(response):
    """Keep browser/dev-server caching from hiding frontend fixes."""
    response.headers["Cache-Control"] = "no-store"
    return response


def _analyze_uploaded_resume(resume, job_description: str) -> dict:
    """Analyze an uploaded resume file and return the report."""
    if not resume or not resume.filename:
        raise ValueError("Please upload a resume file.")
    if not job_description.strip():
        raise ValueError("Please enter a job description.")

    suffix = Path(resume.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        resume.save(temp_file.name)
        temp_path = Path(temp_file.name)

    try:
        resume_text = read_resume_file(temp_path)
        result = analyze_resume(resume_text, job_description)
        save_report_json(result)
        return result
    finally:
        temp_path.unlink(missing_ok=True)


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """JSON endpoint used by the React frontend."""
    resume = request.files.get("resume")
    job_description = request.form.get("job_description", "")

    try:
        result = _analyze_uploaded_resume(resume, job_description)
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error": str(exc), "error_type": type(exc).__name__}), 400


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        resume = request.files.get("resume")
        job_description = request.form.get("job_description", "")

        try:
            result = _analyze_uploaded_resume(resume, job_description)
        except Exception as exc:
            error = str(exc)

    return render_template("index.html", result=result, error=error)


if __name__ == "__main__":
    app.run(debug=True)
