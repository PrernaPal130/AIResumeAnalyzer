import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const emptyResult = null;

function formatList(items) {
  if (!items || items.length === 0) {
    return "None";
  }

  return items.join(", ");
}

function App() {
  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(emptyResult);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const scoreStyle = useMemo(() => {
    const score = result?.match_score ?? 0;
    return {
      background: `conic-gradient(#0f766e ${score * 3.6}deg, #d8dee7 0deg)`,
    };
  }, [result]);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setResult(emptyResult);

    if (!resume) {
      setError("Please upload a TXT or PDF resume.");
      return;
    }

    if (!jobDescription.trim()) {
      setError("Please paste a job description.");
      return;
    }

    const formData = new FormData();
    formData.append("resume", resume);
    formData.append("job_description", jobDescription);

    setIsLoading(true);
    try {
      const response = await fetch(
        "https://airesumeanalyzer-luly.onrender.com/api/analyze",
        {
          method: "POST",
          body: formData,
        },
      );
      const responseText = await response.text();
      let data = {};

      if (responseText) {
        try {
          data = JSON.parse(responseText);
        } catch {
          throw new Error(
            responseText || "The server returned an unreadable response.",
          );
        }
      }

      if (!response.ok) {
        const detail = data.error || responseText || response.statusText;
        throw new Error(`Could not analyze resume: ${detail}`);
      }

      if (!data.match_score && data.match_score !== 0) {
        throw new Error("The server did not return an analysis report.");
      }

      setResult(data);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="workspace">
        <div className="intro">
          <p className="eyebrow">Resume intelligence</p>
          <h1>AI Resume Analyzer</h1>
          <p>
            Upload a resume, paste a job description, and get a practical match
            report with missing skills and keyword coverage.
          </p>
        </div>

        <form className="analyzer-panel" onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="resume">Resume file</label>
            <input
              id="resume"
              type="file"
              accept=".txt,.pdf"
              onChange={(event) => setResume(event.target.files?.[0] || null)}
            />
            <span className="hint">
              {resume ? resume.name : "PDF or TXT accepted"}
            </span>
          </div>

          <div className="field">
            <label htmlFor="job-description">Job description</label>
            <textarea
              id="job-description"
              value={jobDescription}
              onChange={(event) => setJobDescription(event.target.value)}
              placeholder="Paste the full job description here..."
            />
          </div>

          {error && <div className="error">{error}</div>}

          <button className="primary-action" disabled={isLoading} type="submit">
            {isLoading ? "Analyzing..." : "Analyze Resume"}
          </button>
        </form>
      </section>

      <section className="results-area" aria-live="polite">
        {!result && (
          <div className="empty-state">
            <h2>Report Preview</h2>
            <p>
              Your match score, keywords, missing skills, and suggestions will
              appear here.
            </p>
          </div>
        )}

        {result && (
          <>
            <div className="score-panel">
              <div className="score-ring" style={scoreStyle}>
                <span>{result.match_score}%</span>
              </div>
              <div>
                <p className="eyebrow">Match score</p>
                <h2>
                  {result.match_score >= 70
                    ? "Strong fit"
                    : result.match_score >= 45
                      ? "Promising fit"
                      : "Needs tailoring"}
                </h2>
                <p>
                  Text similarity: {result.similarity_score}% | Keyword score:{" "}
                  {result.keyword_score}%
                </p>
                {result.database_id && <p className="save-note">Saved report #{result.database_id}</p>}
                {result.database_warning && <p className="save-warning">{result.database_warning}</p>}
              </div>
            </div>

            <div className="result-grid">
              <article className="result-card">
                <h3>Keywords Found</h3>
                <p>{formatList(result.keywords_found)}</p>
              </article>

              <article className="result-card">
                <h3>Required Skills</h3>
                <p>{formatList(result.required_skills)}</p>
              </article>

              <article className="result-card">
                <h3>Preferred Skills</h3>
                <p>{formatList(result.preferred_skills)}</p>
              </article>

              <article className="result-card warning">
                <h3>Missing Required</h3>
                <p>{formatList(result.missing_required_skills)}</p>
              </article>

              <article className="result-card warning">
                <h3>Missing Preferred</h3>
                <p>{formatList(result.missing_preferred_skills)}</p>
              </article>

              <article className="result-card">
                <h3>Resume Keywords</h3>
                <p>{formatList(result.resume_keywords)}</p>
              </article>

              <article className="result-card">
                <h3>Suggestions</h3>
                <ul>
                  {result.suggestions.map((suggestion) => (
                    <li key={suggestion}>{suggestion}</li>
                  ))}
                </ul>
              </article>
            </div>
          </>
        )}
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
