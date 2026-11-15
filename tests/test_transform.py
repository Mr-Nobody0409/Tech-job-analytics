import pandas as pd
from src.transform import extract_skills
from src.transform import transform_jobs


def test_extract_skills():
    description = """
    We are looking for a Data Engineer with Python,
    SQL, Apache Airflow, Docker and AWS experience.
    """

    skills = extract_skills(description)

    assert "python" in skills
    assert "sql" in skills
    assert "airflow" in skills
    assert "docker" in skills
    assert "aws" in skills

def test_skill_extraction_does_not_match_partial_words():
    description = """
    We need someone who enjoys pythons and mysqlserver.
    """

    skills = extract_skills(description)

    assert "python" not in skills
    assert "mysql" not in skills

def test_duplicate_jobs_are_removed():

    data = [
        {
            "id": 1001,
            "title": "Python Developer",
            "company_name": "Company A",
            "candidate_required_location": "India",
            "category": "Software Development",
            "job_type": "Full-Time",
            "publication_date": "2026-09-01T10:00:00",
            "description": "<p>Python and SQL developer</p>",
            "salary": None
        },
        {
            "id": 1001,  # Same ID → duplicate
            "title": "Python Developer",
            "company_name": "Company A",
            "candidate_required_location": "India",
            "category": "Software Development",
            "job_type": "Full-Time",
            "publication_date": "2026-09-01T10:00:00",
            "description": "<p>Python and SQL developer</p>",
            "salary": None
        }
    ]

    df = pd.DataFrame(data)

    transformed_df = transform_jobs(df)

    assert len(transformed_df) == 1