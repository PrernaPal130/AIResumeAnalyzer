# AI Resume Analyzer

A beginner-friendly Python project that compares a resume with a job description and prints a clean match report.

## Features

- Reads resumes from `.txt` and `.pdf` files
- Accepts job descriptions from pasted text or a `.txt` file
- Extracts PDF text with `pypdf`
- Cleans and preprocesses text
- Uses TF-IDF cosine similarity when `scikit-learn` is installed
- Falls back to a built-in cosine similarity method if `scikit-learn` is unavailable
- Reports match score, missing skills, keywords found, and suggestions
- Separates required skills from preferred or bonus skills when the job description has those sections
- Saves results to `analysis_result.json`
- Includes a Flask API backend
- Includes a React frontend built with Vite
- Can save analysis reports to PostgreSQL when `DATABASE_URL` is configured

## Folder Structure

```text
AIresume/
├── analyzer.py
├── app.py
├── db.py
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── src/
│   │   ├── main.jsx
│   │   └── styles.css
│   └── vite.config.js
├── main.py
├── requirements.txt
├── sample_jd.txt
├── sample_resume.txt
├── templates/
│   └── index.html
└── utils.py
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

The CLI can still run without `scikit-learn`; it will use the fallback similarity method. PDF files require `pypdf`.

## PostgreSQL Setup

The app works without a database, but if `DATABASE_URL` is configured it saves every analysis report to PostgreSQL.

Store these fields:

```text
resume filename
job description
match score
text similarity score
keyword score
keywords found
missing skills
required skills
preferred skills
missing required skills
missing preferred skills
suggestions
full JSON report
created timestamp
```

For local development, set:

```bash
set DATABASE_URL=postgresql://username:password@localhost:5432/ai_resume_analyzer
```

On Render, create a PostgreSQL database and add its `DATABASE_URL` to the Flask web service environment variables.

The app creates the `analysis_reports` table automatically on startup.

Recent saved reports are available at:

```text
/api/history
```

## Run the CLI

```bash
python main.py
```

Choose option `2` to test with the sample resume and sample job description.

## Run the React Frontend

Open one terminal for the Flask API:

```bash
python app.py
```

Open a second terminal for React:

```bash
cd frontend
npm install
npm run dev
```

On Windows PowerShell, if `npm` is blocked by script execution policy, use `npm.cmd` instead:

```bash
npm.cmd install
npm.cmd run dev
```

Then open:

```text
http://127.0.0.1:5173
```

The React dev server proxies `/api/analyze` to the Flask backend at `http://127.0.0.1:5000`.

## Optional Flask Template Page

The older Flask template UI is still available at:

```text
http://127.0.0.1:5000
```

## Example Output

```text
AI Resume Analyzer Report
============================
Match Score: 51%
Text Similarity: 45.34%
Keyword Score: 58.82%
Keywords Found: agile, data analysis, flask, git, numpy, pandas, postgresql, python, rest, sql
Required Skills: agile, communication, data analysis, django, flask, git, numpy, pandas, postgresql, python, rest, sql
Preferred Skills: aws, docker, react, testing, unit testing
Missing Skills: aws, communication, django, docker, react, testing, unit testing
Missing Required Skills: communication, django
Missing Preferred Skills: aws, docker, react, testing, unit testing

Suggested Improvements:
1. Prioritize required skills first: communication, django.
2. Use measurable achievements, such as performance gains, cost savings, users served, or project outcomes.
```
