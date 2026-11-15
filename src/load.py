import ast
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

from config import DATABASE_URL


engine = create_engine(DATABASE_URL)


def load_locations(connection, df):
    """Insert unique locations into locations table."""

    locations = df["location"].dropna().unique()

    for location in locations:

        connection.execute(
            text("""
                INSERT IGNORE INTO locations (location_name)
                VALUES (:location)
            """),
            {
                "location": str(location)
            }
        )


def get_location_mapping(connection):
    """Get location name -> location_id mapping."""

    result = connection.execute(
        text("""
            SELECT location_id, location_name
            FROM locations
        """)
    )

    return {
        row.location_name: row.location_id
        for row in result
    }


def load_jobs(connection, df, location_mapping):
    """Insert jobs into jobs table."""

    for _, row in df.iterrows():

        location_id = location_mapping.get(
            row["location"]
        )

        connection.execute(
            text("""
                INSERT IGNORE INTO jobs (
                    source_job_id,
                    title,
                    company,
                    location_id,
                    category,
                    job_type,
                    description,
                    salary_min,
                    salary_max,
                    published_at
                )
                VALUES (
                    :source_job_id,
                    :title,
                    :company,
                    :location_id,
                    :category,
                    :job_type,
                    :description,
                    :salary_min,
                    :salary_max,
                    :published_at
                )
            """),
            {
                "source_job_id": int(
                    row["source_job_id"]
                ),
                "title": row["title"],
                "company": row["company"],
                "location_id": location_id,
                "category": row["category"],
                "job_type": row["job_type"],
                "description": row["description"],
                "salary_min": (
                    None
                    if pd.isna(row["salary_min"])
                    else float(row["salary_min"])
                ),
                "salary_max": (
                    None
                    if pd.isna(row["salary_max"])
                    else float(row["salary_max"])
                ),
                "published_at": row["published_at"]
            }
        )


def load_skills(connection, df):
    """Insert unique skills."""

    unique_skills = set()

    for skills in df["skills"]:

        if pd.isna(skills):
            continue

        # CSV stores Python lists as strings
        if isinstance(skills, str):
            skills = ast.literal_eval(skills)

        for skill in skills:
            unique_skills.add(skill)

    for skill in unique_skills:

        connection.execute(
            text("""
                INSERT IGNORE INTO skills (
                    skill_name
                )
                VALUES (:skill)
            """),
            {
                "skill": skill
            }
        )


def get_job_mapping(connection):
    """Get source_job_id -> job_id mapping."""

    result = connection.execute(
        text("""
            SELECT job_id, source_job_id
            FROM jobs
        """)
    )

    return {
        row.source_job_id: row.job_id
        for row in result
    }


def get_skill_mapping(connection):
    """Get skill_name -> skill_id mapping."""

    result = connection.execute(
        text("""
            SELECT skill_id, skill_name
            FROM skills
        """)
    )

    return {
        row.skill_name: row.skill_id
        for row in result
    }


def load_job_skills(
    connection,
    df,
    job_mapping,
    skill_mapping
):
    """Insert many-to-many job-skill relationships."""

    for _, row in df.iterrows():

        source_job_id = int(
            row["source_job_id"]
        )

        job_id = job_mapping.get(
            source_job_id
        )

        if not job_id:
            continue

        skills = row["skills"]

        if pd.isna(skills):
            continue

        if isinstance(skills, str):
            skills = ast.literal_eval(skills)

        for skill in skills:

            skill_id = skill_mapping.get(
                skill
            )

            if not skill_id:
                continue

            connection.execute(
                text("""
                    INSERT IGNORE INTO job_skills (
                        job_id,
                        skill_id
                    )
                    VALUES (
                        :job_id,
                        :skill_id
                    )
                """),
                {
                    "job_id": job_id,
                    "skill_id": skill_id
                }
            )


def main(file_path):

    df = pd.read_csv(file_path)

    df["published_at"] = pd.to_datetime(
        df["published_at"],
        errors="coerce"
    )

    print(
        f"Loaded {len(df)} jobs from CSV"
    )

    with engine.begin() as connection:

        print("Loading locations...")

        load_locations(
            connection,
            df
        )

        location_mapping = (
            get_location_mapping(
                connection
            )
        )

        print("Loading jobs...")

        load_jobs(
            connection,
            df,
            location_mapping
        )

        print("Loading skills...")

        load_skills(
            connection,
            df
        )

        job_mapping = (
            get_job_mapping(
                connection
            )
        )

        skill_mapping = (
            get_skill_mapping(
                connection
            )
        )

        print(
            "Loading job-skill relationships..."
        )

        load_job_skills(
            connection,
            df,
            job_mapping,
            skill_mapping
        )

    print(
        "Data loaded successfully!"
    )


if __name__ == "__main__":

    file_path = Path(
        "data/processed/jobs_cleaned.csv"
    )

    main(file_path)