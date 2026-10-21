"""Resume vs job-description scoring engine.

Fully local and deterministic: no API calls, no ML models. It works in three
steps:

1. Extract skills from both texts using the static lexicon in skills.py.
2. Score four dimensions: skill coverage, section completeness, quantified
   achievements, and resume length.
3. Turn the results into a ranked tip list.

Nothing here is a real ATS — it is a coaching tool that tells you what a
matching algorithm is likely to notice.
"""

import re

from skills import SKILLS

# Sections we expect on a typical data/AI resume. Each entry is
# (display name, regex matched against short lines only).
SECTIONS = [
    ("Summary", r"^(professional\s+)?(career\s+)?summary|objective|profile$"),
    ("Experience", r"^((professional|work)\s+)?experience|employment(\s+history)?$"),
    ("Projects", r"^projects?$"),
    ("Skills", r"^(technical\s+|core\s+)?skills|core\s+competencies|technologies$"),
    ("Education", r"^education|academic\s+background$"),
    ("Certifications", r"^certifications?|licenses?$"),
]

# A line counts as a section header only if it is short (under 6 words).
_MAX_HEADER_WORDS = 6

# Quantified-achievement patterns: numbers tied to impact words, money,
# percentages, or explicit multipliers.
_METRIC_PATTERNS = [
    r"\$\s?\d[\d,]*(?:\.\d+)?(?:\s?[KMB])?",          # $12K, $4.2M, $50,000
    r"\b\d[\d,]*(?:\.\d+)?\s?%",                       # 38%
    r"\b\d+(?:\.\d+)?\s?x\b",                          # 3x faster
    r"\b(?:increased|improved|reduced|cut|grew|growing|saved|boosted|lifted|"
    r"dropped|decreased|scaled|automated|accelerated)\b.{0,40}?\b\d[\d,]*(?:\.\d+)?",
    r"\b\d[\d,]*\s?(?:users|customers|rows|records|transactions|orders|"
    r"requests|tickets|models|features|tables|pipelines|dashboards|reports)\b",
]


def find_skills(text):
    """Return the sorted list of lexicon skills present in text (case-insensitive)."""
    found = set()
    for skill in SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern, text, re.IGNORECASE):
            found.add(skill)
    return sorted(found)


def detect_sections(text):
    """Return {section_name: True/False} based on short header-like lines."""
    present = {name: False for name, _ in SECTIONS}
    for line in text.splitlines():
        stripped = line.strip().strip("#:*-").strip()
        if not stripped or len(stripped.split()) > _MAX_HEADER_WORDS:
            continue
        for name, pattern in SECTIONS:
            if re.search(pattern, stripped, re.IGNORECASE):
                present[name] = True
    return present


def count_metric_hits(text):
    """Count distinct quantified-achievement patterns in the text."""
    lowered = text.lower()
    hits = 0
    for pattern in _METRIC_PATTERNS:
        hits += len(re.findall(pattern, lowered))
    return hits


def length_score(words):
    """Score resume length; the 400-1000 word range scores full marks."""
    if words < 400:
        return words / 400
    if words > 1000:
        return max(0.3, 1.0 - (words - 1000) / 2500)
    return 1.0


def build_tips(analysis):
    """Turn the analysis numbers into a readable, prioritized tip list."""
    tips = []

    coverage = analysis["coverage"]
    if coverage < 1.0 and analysis["missing_skills"]:
        shown = ", ".join(analysis["missing_skills"][:6])
        tail = f" (+{len(analysis['missing_skills']) - 6} more)" if len(analysis["missing_skills"]) > 6 else ""
        tips.append({
            "title": "Close the keyword gap",
            "body": f"The posting names {len(analysis['required_skills'])} skills and "
                    f"{coverage:.0%} of them appear on the resume. If you genuinely have "
                    f"them, add these where they belong: {shown}{tail}.",
            "priority": "high" if coverage < 0.6 else "medium",
        })

    for name, present in analysis["sections"].items():
        if not present:
            tips.append({
                "title": f"Add a {name} section",
                "body": f"No {name.lower()} section was detected. Most data resumes "
                        "benefit from one — it is cheap keyword real estate.",
                "priority": "medium" if name in ("Projects", "Summary") else "low",
            })

    if analysis["metric_hits"] < 3:
        tips.append({
            "title": "Quantify more achievements",
            "body": "Only a few results are tied to numbers. Hiring managers and "
                    "scoring tools both reward bullets like \"cut dashboard load time "
                    "38%\" over \"improved dashboards\".",
            "priority": "high",
        })

    words = analysis["word_count"]
    if words < 400:
        tips.append({
            "title": "Resume looks thin",
            "body": f"About {words} words — one page with a bit more substance "
                    "usually scores better. Expand 2-3 strongest bullets.",
            "priority": "medium",
        })
    elif words > 1000:
        tips.append({
            "title": "Resume may be too long",
            "body": f"About {words} words — beyond one to two pages the signal gets "
                    "diluted. Trim the oldest or least relevant bullets.",
            "priority": "medium",
        })

    if not tips:
        tips.append({
            "title": "Strong match",
            "body": "Coverage, sections and quantification all look solid for this "
                    "posting. Final polish: mirror the posting's exact phrasing "
                    "(e.g. \"A/B testing\" vs \"experimentation\") for the top 3 skills.",
            "priority": "low",
        })

    order = {"high": 0, "medium": 1, "low": 2}
    return sorted(tips, key=lambda t: order[t["priority"]])


def analyze(resume_text, jd_text):
    """Run the full analysis. Returns a plain dict ready for JSON or templates."""
    resume_text = resume_text or ""
    jd_text = jd_text or ""

    required = find_skills(jd_text)
    resume_skills = find_skills(resume_text)
    required_set, resume_set = set(required), set(resume_skills)
    matched = sorted(required_set & resume_set)
    missing = sorted(required_set - resume_set)
    coverage = len(matched) / len(required) if required else 0.0

    sections = detect_sections(resume_text)
    section_score = sum(sections.values()) / len(sections)

    metric_hits = count_metric_hits(resume_text)
    metric_score = min(metric_hits / 8, 1.0)

    words = len(re.findall(r"\w+", resume_text))
    len_score = length_score(words)

    overall = round(45 * coverage + 25 * section_score + 15 * metric_score + 15 * len_score)

    analysis = {
        "score": overall,
        "coverage": coverage,
        "required_skills": required,
        "resume_skills": resume_skills,
        "matched_skills": matched,
        "missing_skills": missing,
        "sections": sections,
        "metric_hits": metric_hits,
        "word_count": words,
        "breakdown": [
            {"label": "Skill coverage", "value": round(45 * coverage, 1), "max": 45},
            {"label": "Sections", "value": round(25 * section_score, 1), "max": 25},
            {"label": "Quantified results", "value": round(15 * metric_score, 1), "max": 15},
            {"label": "Length", "value": round(15 * len_score, 1), "max": 15},
        ],
    }
    analysis["tips"] = build_tips(analysis)
    return analysis
