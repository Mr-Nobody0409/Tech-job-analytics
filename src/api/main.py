from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Query
from sqlalchemy import create_engine, text

from config import DATABASE_URL


app = FastAPI(
    title="Tech Job Analytics API",
    description="API for analyzing technology job postings",
    version="1.0.0"
)


engine = create_engine(DATABASE_URL)


@app.get("/")
def home():

    return {
        "message": "Tech Job Analytics API is running"
    }


@app.get("/health")
def health_check():

    try:

        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT 1")
            )

            result.scalar()

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as error:

        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(error)
        }


@app.get("/jobs/top-skills")
def get_top_skills(
    limit: int = Query(
        default=10,
        ge=1,
        le=50
    )
):

    query = text("""
        SELECT
            s.skill_name,
            COUNT(*) AS job_count
        FROM skills s
        JOIN job_skills js
            ON s.skill_id = js.skill_id
        GROUP BY s.skill_id, s.skill_name
        ORDER BY job_count DESC
        LIMIT :limit
    """)

    with engine.connect() as connection:

        result = connection.execute(
            query,
            {"limit": limit}
        )

        skills = [
            {
                "skill": row.skill_name,
                "job_count": row.job_count
            }
            for row in result
        ]

    return {
        "total_results": len(skills),
        "data": skills
    }


@app.get("/jobs/by-location")
def get_jobs_by_location(
    limit: int = Query(
        default=10,
        ge=1,
        le=50
    )
):

    query = text("""
        SELECT
            l.location_name,
            COUNT(j.job_id) AS job_count
        FROM locations l
        LEFT JOIN jobs j
            ON l.location_id = j.location_id
        GROUP BY l.location_id, l.location_name
        ORDER BY job_count DESC
        LIMIT :limit
    """)

    with engine.connect() as connection:

        result = connection.execute(
            query,
            {"limit": limit}
        )

        locations = [
            {
                "location": row.location_name,
                "job_count": row.job_count
            }
            for row in result
        ]

    return {
        "total_results": len(locations),
        "data": locations
    }


@app.get("/jobs/trends")
def get_job_trends(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):

    query = """
        SELECT
            DATE(published_at) AS date,
            COUNT(*) AS job_count
        FROM jobs
        WHERE published_at IS NOT NULL
    """

    parameters = {}

    if start_date:

        query += """
            AND published_at >= :start_date
        """

        parameters["start_date"] = start_date

    if end_date:

        query += """
            AND published_at <= :end_date
        """

        parameters["end_date"] = end_date

    query += """
        GROUP BY DATE(published_at)
        ORDER BY date
    """

    with engine.connect() as connection:

        result = connection.execute(
            text(query),
            parameters
        )

        trends = [
            {
                "date": str(row.date),
                "job_count": row.job_count
            }
            for row in result
        ]

    return {
        "total_results": len(trends),
        "data": trends
    }