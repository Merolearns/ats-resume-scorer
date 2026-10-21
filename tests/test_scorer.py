import re

import pytest

from scorer import (
    analyze,
    build_tips,
    count_metric_hits,
    detect_sections,
    find_skills,
    length_score,
)


def test_find_skills_matches_phrases_case_insensitively():
    found = find_skills("I know Python, SQL and Machine Learning well.")
    assert "python" in found
    assert "sql" in found
    assert "machine learning" in found
    assert "rust" not in found


def test_find_skills_respects_word_boundaries():
    # "go" should not match inside "going", but "c++" should match literally
    found = find_skills("I am going to learn C++ soon.")
    assert "go" not in found
    assert "c++" in found


def test_detect_sections_finds_headers_not_body_text():
    text = "SUMMARY\nSenior analyst with 5 years.\nEXPERIENCE\nAnalyst at X."
    sections = detect_sections(text)
    assert sections["Summary"] is True
    assert sections["Experience"] is True
    assert sections["Projects"] is False


def test_detect_sections_ignores_long_lines():
    # A bullet that merely mentions "experience" should not count as a header
    text = "Five years of experience building dashboards and reports for clients."
    assert detect_sections(text)["Experience"] is False


def test_count_metric_hits_counts_quantified_achievements():
    text = "Cut load time 38%. Saved $12K. Improved speed 3x."
    assert count_metric_hits(text) >= 3


def test_count_metric_hits_zero_on_vague_bullets():
    text = "Responsible for dashboards. Worked with stakeholders daily."
    assert count_metric_hits(text) == 0


def test_length_score_sweet_spot():
    assert length_score(600) == 1.0
    assert length_score(400) == 1.0
    assert length_score(1000) == 1.0


def test_length_score_penalties():
    assert length_score(200) == pytest.approx(0.5)
    assert length_score(2000) < 1.0
    assert length_score(10000) == pytest.approx(0.3)


def test_analyze_perfect_match_scores_high():
    jd = "We need Python, SQL and pandas."
    resume = (
        "SUMMARY\nPython analyst with 5 years of experience.\n"
        "EXPERIENCE\nUsed Python, SQL and pandas daily at Acme Corp. "
        "Cut report generation time 40% and saved $30K annually.\n"
        "PROJECTS\nChurn dashboard built with pandas and SQL.\n"
        "SKILLS\nPython, SQL, pandas\n"
        "EDUCATION\nBS Computer Science, State University, 2020\n"
        "CERTIFICATIONS\nAWS Cloud Practitioner."
    )
    result = analyze(resume, jd)
    assert result["coverage"] == 1.0
    assert result["matched_skills"] == ["pandas", "python", "sql"]
    assert result["missing_skills"] == []
    assert result["score"] >= 60


def test_analyze_empty_inputs_does_not_crash():
    result = analyze("", "")
    assert result["score"] == 0
    assert result["tips"]  # still offers advice


def test_analyze_breakdown_sums_to_score():
    result = analyze("Python and SQL experience.", "We need Python, SQL, R, Spark.")
    total = sum(item["value"] for item in result["breakdown"])
    assert round(total) == result["score"]


def test_build_tips_surfaces_missing_skills_first():
    analysis = analyze("I like dogs.", "Need Python, SQL, Airflow, dbt.")
    tips = build_tips(analysis)
    assert tips[0]["title"] == "Close the keyword gap"
    assert tips[0]["priority"] == "high"


def test_build_tips_celebrates_strong_match():
    resume = (
        "SUMMARY\nData analyst.\nEXPERIENCE\nBuilt ETL with Python, SQL and Airflow. "
        "Cut costs 20% and saved $50K.\nPROJECTS\nChurn model.\nSKILLS\nPython, SQL\n"
        "EDUCATION\nBS\nCERTIFICATIONS\nAWS.\n" + "Python SQL analysis. " * 150
    )
    tips = build_tips(analyze(resume, "Need Python and SQL."))
    assert any(t["title"] == "Strong match" for t in tips)


def test_sample_pair_produces_reported_score():
    import os

    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(here, "samples", "sample_resume.txt")) as f:
        resume = f.read()
    with open(os.path.join(here, "samples", "sample_job_description.txt")) as f:
        jd = f.read()
    result = analyze(resume, jd)
    # Honest regression check against the README example output
    assert result["score"] == 62
    assert round(result["coverage"], 2) == 0.55
