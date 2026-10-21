# ats-resume-scorer

Paste a resume and a job description, get a visual match report. The app runs
entirely on your machine — nothing is uploaded or stored.

I built this to learn how keyword-based resume matching actually works, the
way applicant tracking systems do it. The whole pipeline — skill extraction,
section detection, scoring — is plain Python you can read, and every number
in the report is computed live, not mocked.

## How it works

1. **Skill extraction** — a static lexicon of ~120 data/AI/engineering skills
   (`skills.py`) is matched case-insensitively against both texts.
2. **Section detection** — the resume is scanned for short header lines like
   Summary, Experience, Projects, Skills, Education, Certifications.
3. **Scoring (100 points)** —
   - Skill coverage (45): share of the posting's required skills found on the resume
   - Sections (25): which standard sections are present
   - Quantified results (15): bullets tied to numbers ($, %, 3x, "cut load time 38%")
   - Length (15): full marks in the 400–1000 word range
4. **Tips** — rule-based, priority-ordered advice derived from the gaps found.

There is also a JSON API (`POST /api/analyze`) for programmatic use.

## Run it

```bash
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 — or click **Load sample resume** and
**Load sample posting** on the page to try it with the included fixtures
in `samples/` (a fictional data-analyst resume and a fictional job posting).

## Example output

Running the included samples through the app produces this report
(score 62/100):

- **Match verdict:** Good match, room to improve
- **Skill coverage:** 11 of 20 required skills found (55%) — matched: airflow,
  data warehouse, dbt, pandas, power bi, python, regression, snowflake, sql,
  storytelling, tableau
- **Missing skills:** aws, data analysis, data engineering, experimental
  design, forecasting, gcp, hypothesis testing, machine learning,
  stakeholder communication
- **Breakdown:** Skill coverage 24.8/45 · Sections 20.8/25 · Quantified
  results 7.5/15 · Length 8.7/15
- **Section check:** Summary, Experience, Projects, Skills, Education found;
  Certifications missing
- **Tips (in order):** Close the keyword gap (high) · Resume looks thin —
  231 words (medium) · Add a Certifications section (low)

The repo ships with a regression test (`test_sample_pair_produces_reported_score`)
that re-runs this fixture pair and asserts these exact numbers.

## Honest limitations

- It is a coaching tool, not a real ATS. Real systems weigh recency,
  titles, and semantics this tool does not model.
- Skill extraction is literal keyword matching — it will not recognize
  synonyms ("experimentation" vs "A/B testing") or context.
- Scores are relative to the static lexicon, so compare scores only between
  postings, not as absolutes.

## Run the tests

```bash
pip install -r requirements.txt
python -m pytest
```
