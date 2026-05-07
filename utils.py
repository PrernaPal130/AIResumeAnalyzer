"""Text processing helpers for AI Resume Analyzer."""

from __future__ import annotations

import re
from pathlib import Path


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "our",
    "that",
    "the",
    "this",
    "to",
    "with",
    "you",
    "your",
}


SKILL_KEYWORDS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "node",
    "node.js",
    "flask",
    "django",
    "fastapi",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "git",
    "linux",
    "html",
    "css",
    "api",
    "rest",
    "graphql",
    "machine learning",
    "nlp",
    "data analysis",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "excel",
    "power bi",
    "tableau",
    "communication",
    "leadership",
    "agile",
    "scrum",
    "testing",
    "unit testing",
    "ci/cd",
}

SKILL_ALIASES = {
    "react": {"react", "react.js", "reactjs"},
    "node": {"node", "node.js", "nodejs"},
    "javascript": {"javascript", "java script"},
    "typescript": {"typescript", "type script"},
    "postgresql": {"postgresql", "postgres", "postgres sql"},
    "scikit-learn": {"scikit-learn", "scikit learn", "sklearn"},
    "machine learning": {"machine learning", "ml"},
    "rest": {"rest", "rest api", "restful"},
    "ci/cd": {"ci/cd", "cicd", "ci cd"},
    "git": {"git", "github", "gitlab", "bitbucket"},
}


def read_text_file(file_path: str | Path) -> str:
    """Read a UTF-8 text file and return its contents."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_text(encoding="utf-8")


def extract_pdf_text(file_path: str | Path) -> str:
    """Extract text from a PDF using pypdf."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ImportError(
            "PDF support requires pypdf. Install it with: pip install pypdf"
        ) from exc

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")

    text = "\n".join(pages).strip()
    if not text:
        raise ValueError("No readable text was found in the PDF.")
    return text


def read_resume_file(file_path: str | Path) -> str:
    """Read a resume from TXT or PDF."""
    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".txt":
        return read_text_file(path)
    if extension == ".pdf":
        return extract_pdf_text(path)

    raise ValueError("Unsupported resume format. Please use a .txt or .pdf file.")


def clean_text(text: str) -> str:
    """Normalize text for comparison."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#./\s-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text: str) -> list[str]:
    """Split text into meaningful tokens and remove common stopwords."""
    cleaned = clean_text(text)
    words = cleaned.split()
    return [word for word in words if word not in STOPWORDS and len(word) > 1]


def extract_keywords(text: str, known_skills: set[str] | None = None) -> set[str]:
    """Find known technical and professional keywords in text."""
    skills = known_skills or SKILL_KEYWORDS
    cleaned = f" {clean_text(text)} "
    found = set()

    for skill in skills:
        aliases = SKILL_ALIASES.get(skill, {skill})
        for alias in aliases:
            alias_pattern = re.escape(alias.lower()).replace(r"\ ", r"\s+")
            if re.search(rf"(?<![a-z0-9+#]){alias_pattern}(?![a-z0-9+#])", cleaned):
                found.add(skill)
                break

    return found


def split_job_description_sections(job_description: str) -> dict[str, str]:
    """Split a job description into required and preferred text blocks."""
    required_markers = (
        "requirement",
        "requirements",
        "required",
        "must have",
        "must-have",
        "mandatory",
        "qualification",
        "qualifications",
        "responsibilities",
        "you will",
        "what you will do",
    )
    preferred_markers = (
        "preferred",
        "nice to have",
        "nice-to-have",
        "bonus",
        "good to have",
        "good-to-have",
        "plus",
        "desirable",
    )

    sections = {"required": [], "preferred": [], "general": []}
    current_section = "general"

    for raw_line in job_description.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        normalized = clean_text(line).strip(" :-")
        heading = normalized[:80]

        if any(marker in heading for marker in preferred_markers):
            current_section = "preferred"
            remainder = re.sub(
                r"^(preferred|nice[-\s]?to[-\s]?have|bonus|good[-\s]?to[-\s]?have|plus|desirable)\s*[:.-]?\s*",
                "",
                line,
                flags=re.IGNORECASE,
            ).strip()
            if remainder:
                sections[current_section].append(remainder)
            continue

        if any(marker in heading for marker in required_markers):
            current_section = "required"
            remainder = re.sub(
                r"^(requirements?|required|must[-\s]?have|mandatory|qualifications?|responsibilities|you will|what you will do)\s*[:.-]?\s*",
                "",
                line,
                flags=re.IGNORECASE,
            ).strip()
            if remainder:
                sections[current_section].append(remainder)
            continue

        sections[current_section].append(line)

    required_text = "\n".join(sections["required"]).strip()
    preferred_text = "\n".join(sections["preferred"]).strip()

    # If the JD has no explicit required section, treat non-preferred text as required.
    if not required_text:
        required_text = "\n".join(sections["general"]).strip()
    elif sections["general"]:
        required_text = "\n".join([*sections["general"], required_text]).strip()

    return {
        "required": required_text,
        "preferred": preferred_text,
    }


def format_skill_list(skills: set[str] | list[str]) -> str:
    """Return a readable comma-separated skill list."""
    if not skills:
        return "None"
    return ", ".join(sorted(skills, key=str.lower))
