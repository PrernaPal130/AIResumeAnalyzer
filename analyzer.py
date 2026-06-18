"""Main analysis logic for AI Resume Analyzer."""

from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path

from utils import (
    extract_keywords,
    format_skill_list,
    split_job_description_sections,
    tokenize,
)


def _manual_cosine_similarity(resume_text: str, job_description: str) -> float:
    """Calculate cosine similarity without third-party libraries."""
    resume_tokens = tokenize(resume_text)
    jd_tokens = tokenize(job_description)

    if not resume_tokens or not jd_tokens:
        return 0.0

    resume_counts = Counter(resume_tokens)
    jd_counts = Counter(jd_tokens)
    vocabulary = set(resume_counts) | set(jd_counts)

    dot_product = sum(resume_counts[word] * jd_counts[word] for word in vocabulary)
    resume_magnitude = math.sqrt(sum(count * count for count in resume_counts.values()))
    jd_magnitude = math.sqrt(sum(count * count for count in jd_counts.values()))

    if resume_magnitude == 0 or jd_magnitude == 0:
        return 0.0

    return dot_product / (resume_magnitude * jd_magnitude)


def _tfidf_similarity(resume_text: str, job_description: str) -> float:
    """Calculate TF-IDF cosine similarity, falling back to manual cosine."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError:
        return _manual_cosine_similarity(resume_text, job_description)

    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform([resume_text, job_description])
    return float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])


def generate_suggestions(
    resume_keywords: set[str],
    jd_keywords: set[str],
    missing_skills: set[str],
    missing_required_skills: set[str] | None = None,
) -> list[str]:
    """Create beginner-friendly improvement suggestions."""
    suggestions = []

    missing_required_skills = missing_required_skills or set()

    if missing_required_skills:
        suggestions.append(
            f"Prioritize required skills first: {format_skill_list(missing_required_skills)}."
        )
    elif missing_skills:
        suggestions.append(
            f"Add relevant experience or projects that mention: {format_skill_list(missing_skills)}."
        )

    if len(resume_keywords) < 5:
        suggestions.append(
            "Include a dedicated skills section with tools, frameworks, databases, and methods."
        )

    if jd_keywords and len(resume_keywords & jd_keywords) / len(jd_keywords) < 0.5:
        suggestions.append(
            "Mirror important job-description keywords naturally in your summary and bullet points."
        )

    suggestions.append(
        "Use measurable achievements, such as performance gains, cost savings, users served, or project outcomes."
    )

    return suggestions


def analyze_resume(resume_text: str, job_description: str) -> dict:
    """Analyze resume text against a job description."""
    if not resume_text.strip():
        raise ValueError("Resume text is empty.")
    if not job_description.strip():
        raise ValueError("Job description is empty.")

    similarity = _tfidf_similarity(resume_text, job_description)
    jd_sections = split_job_description_sections(job_description)
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(job_description)
    required_skills = extract_keywords(jd_sections["required"])
    preferred_skills = extract_keywords(jd_sections["preferred"])
    common_keywords = resume_keywords & jd_keywords
    missing_skills = jd_keywords - resume_keywords
    missing_required_skills = required_skills - resume_keywords
    missing_preferred_skills = preferred_skills - resume_keywords

    keyword_score = len(common_keywords) / len(jd_keywords) if jd_keywords else 0
    required_score = (
        len(required_skills & resume_keywords) / len(required_skills)
        if required_skills
        else keyword_score
    )
    preferred_score = (
        len(preferred_skills & resume_keywords) / len(preferred_skills)
        if preferred_skills
        else keyword_score
    )

    # Prioritize recruiter-style skill fit over broad text similarity.
    match_score = round(
        (
            (required_score * 0.50)
            + (preferred_score * 0.25)
            + (keyword_score * 0.15)
            + (similarity * 0.10)
        )
        * 100
    )
    match_score = max(0, min(100, match_score))

    return {
        "match_score": match_score,
        "similarity_score": round(similarity * 100, 2),
        "keyword_score": round(keyword_score * 100, 2),
        "required_score": round(required_score * 100, 2),
        "preferred_score": round(preferred_score * 100, 2),
        "keywords_found": sorted(common_keywords),
        "resume_keywords": sorted(resume_keywords),
        "job_description_keywords": sorted(jd_keywords),
        "required_skills": sorted(required_skills),
        "preferred_skills": sorted(preferred_skills),
        "missing_skills": sorted(missing_skills),
        "missing_required_skills": sorted(missing_required_skills),
        "missing_preferred_skills": sorted(missing_preferred_skills),
        "suggestions": generate_suggestions(
            resume_keywords, jd_keywords, missing_skills, missing_required_skills
        ),
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }


def print_report(result: dict) -> None:
    """Print a clean terminal report."""
    print("\nAI Resume Analyzer Report")
    print("=" * 28)
    print(f"Match Score: {result['match_score']}%")
    print(f"Text Similarity: {result['similarity_score']}%")
    print(f"Keyword Score: {result['keyword_score']}%")
    print(f"Required Skills Score: {result['required_score']}%")
    print(f"Preferred Skills Score: {result['preferred_score']}%")
    print(f"Keywords Found: {format_skill_list(set(result['keywords_found']))}")
    print(f"Required Skills: {format_skill_list(set(result['required_skills']))}")
    print(f"Preferred Skills: {format_skill_list(set(result['preferred_skills']))}")
    print(f"Missing Skills: {format_skill_list(set(result['missing_skills']))}")
    print(
        f"Missing Required Skills: {format_skill_list(set(result['missing_required_skills']))}"
    )
    print(
        f"Missing Preferred Skills: {format_skill_list(set(result['missing_preferred_skills']))}"
    )
    print("\nSuggested Improvements:")
    for index, suggestion in enumerate(result["suggestions"], start=1):
        print(f"{index}. {suggestion}")
    print()


def save_report_json(result: dict, output_path: str | Path = "analysis_result.json") -> Path:
    """Save the analysis report as JSON."""
    path = Path(output_path)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return path
