import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const emptyResult = null;
const apiUrl = "https://airesumeanalyzer-luly.onrender.com/api/analyze";

function SkillChips({ items, tone = "default" }) {
  if (!items || items.length === 0) {
    return <span className="muted-text">None detected</span>;
  }

  return (
    <div className="chip-row">
      {items.map((item) => (
        <span className={`chip ${tone}`} key={item}>
          {item}
        </span>
      ))}
    </div>
  );
}

function MetricCard({ label, value, detail }) {
  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </article>
  );
}

function fitLabel(score) {
  if (score >= 75) return "Excellent fit";
  if (score >= 55) return "Strong potential";
  if (score >= 35) return "Needs targeted edits";
  return "Major tailoring needed";
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
      const response = await fetch(apiUrl, {
        method: "POST",
        body: formData,
      });
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
      <header className="topbar">
        <div className="brand-mark">AI</div>
        <div>
          <p className="eyebrow">Resume intelligence</p>
          <h1>AI Resume Analyzer</h1>
        </div>
      </header>

      <section className="hero-panel">
        <div className="hero-copy">
          <h2>Match a resume to a role in seconds.</h2>
          <p>
            Upload a resume, paste a job description, and get a recruiter-style
            breakdown of match score, required skills, preferred skills, and
            missing keywords.
          </p>
        </div>
        <div className="hero-stats" aria-label="Feature summary">
          <span>PDF/TXT parsing</span>
          <span>TF-IDF scoring</span>
          <span>PostgreSQL history</span>
        </div>
      </section>

      <section className="workspace">
        <form className="analyzer-panel" onSubmit={handleSubmit}>
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Input</p>
              <h2>Analyze candidate fit</h2>
            </div>
            <span className="status-pill">Live API</span>
          </div>

          <div className="field">
            <label htmlFor="resume">Resume file</label>
            <label className="upload-box" htmlFor="resume">
              <input
                id="resume"
                type="file"
                accept=".txt,.pdf"
                onChange={(event) => setResume(event.target.files?.[0] || null)}
              />
              <span className="upload-title">
                {resume ? resume.name : "Choose a resume"}
              </span>
              <span className="hint">PDF or TXT accepted</span>
            </label>
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
            {isLoading ? "Analyzing resume..." : "Analyze Resume"}
          </button>
        </form>

        <section className="results-area" aria-live="polite">
          {!result && (
            <div className="empty-state">
              <div className="empty-visual">%</div>
              <h2>Report preview</h2>
              <p>
                The finished report will highlight score, matched skills,
                missing required skills, and improvement suggestions.
              </p>
              <div className="preview-list">
                <span>Match score</span>
                <span>Skill gaps</span>
                <span>Suggestions</span>
              </div>
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
                  <h2>{fitLabel(result.match_score)}</h2>
                  <p>
                    Required: {result.required_score}% | Preferred:{" "}
                    {result.preferred_score}% | Keywords: {result.keyword_score}%
                  </p>
                  {result.database_id && (
                    <p className="save-note">Saved report #{result.database_id}</p>
                  )}
                  {result.database_warning && (
                    <p className="save-warning">{result.database_warning}</p>
                  )}
                </div>
              </div>

              <div className="metrics-grid">
                <MetricCard
                  label="Required score"
                  value={`${result.required_score ?? 0}%`}
                  detail="50% of the final score"
                />
                <MetricCard
                  label="Preferred score"
                  value={`${result.preferred_score ?? 0}%`}
                  detail="25% of the final score"
                />
                <MetricCard
                  label="Text similarity"
                  value={`${result.similarity_score ?? 0}%`}
                  detail="10% of the final score"
                />
              </div>

              <div className="result-grid">
                <article className="result-card success">
                  <h3>Keywords Found</h3>
                  <SkillChips items={result.keywords_found} tone="success" />
                </article>

                <article className="result-card">
                  <h3>Required Skills</h3>
                  <SkillChips items={result.required_skills} />
                </article>

                <article className="result-card">
                  <h3>Preferred Skills</h3>
                  <SkillChips items={result.preferred_skills} tone="info" />
                </article>

                <article className="result-card warning">
                  <h3>Missing Required</h3>
                  <SkillChips
                    items={result.missing_required_skills}
                    tone="warning"
                  />
                </article>

                <article className="result-card soft-warning">
                  <h3>Missing Preferred</h3>
                  <SkillChips
                    items={result.missing_preferred_skills}
                    tone="warning"
                  />
                </article>

                <article className="result-card">
                  <h3>Resume Keywords</h3>
                  <SkillChips items={result.resume_keywords} tone="neutral" />
                </article>

                <article className="result-card suggestions">
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
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
