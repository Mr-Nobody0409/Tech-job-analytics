# Tech Job Analytics Pipeline

An end-to-end data engineering portfolio project that collects
technology job postings, transforms them with Python and Pandas, loads
them into MySQL, and orchestrates the workflow with Apache Airflow.
Power BI is the planned final reporting layer.

> **Note:** Sample outputs and historical row counts in this README are
> illustrative/reference values, not live system results. Replace them
> with fresh outputs from your environment before claiming current
> status.

## Project goals

-   Extract job postings from the Remotive public jobs API.
-   Save raw responses as dated JSON files.
-   Clean and normalize job data using Python and Pandas.
-   Extract technical skills using keyword dictionaries and regular
    expressions.
-   Deduplicate records and load them into MySQL.
-   Orchestrate scheduled ETL runs with Apache Airflow.
-   Analyze jobs, skills, locations, and available salary information in
    Power BI.

## Technology stack

  Layer            Technology
  ---------------- ----------------------------------
  Language         Python
  Source           Remotive Jobs API
  Transformation   Pandas, regular expressions
  Database         MySQL 8
  Orchestration    Apache Airflow
  Containers       Docker, Docker Compose
  Testing          pytest
  Reporting        Power BI (final reporting layer)

## Architecture

``` text
Remotive Jobs API
       |
       v
 Python extraction
       |
       v
 data/raw/*.json
       |
       v
 Pandas transformation
 (cleaning, title normalization,
 skill extraction, deduplication)
       |
       v
 data/processed/*.csv
       |
       v
 MySQL
 ├── jobs
 ├── locations
 ├── skills
 └── job_skills
       |
       v
 Apache Airflow orchestration
       |
       v
 Power BI dashboard
```

## Repository structure

``` text
tech-job-analytics/
├── airflow/
│   ├── dags/
│   └── Dockerfile
├── data/
│   ├── raw/              # Generated JSON; excluded from Git
│   └── processed/        # Generated CSV; excluded from Git
├── sql/
│   └── schema.sql
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   ├── pipeline.py
│   └── config.py
├── tests/
├── .dockerignore
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

The exact filenames may evolve. Check the repository for the current
layout.

## Database design

  -----------------------------------------------------------------------
  Table                               Purpose
  ----------------------------------- -----------------------------------
  `jobs`                              Job posting details, company,
                                      title, description, salary fields,
                                      publication date, and location
                                      reference

  `locations`                         Normalized job locations

  `skills`                            Unique technical skills extracted
                                      from job descriptions

  `job_skills`                        Many-to-many relationship between
                                      jobs and skills
  -----------------------------------------------------------------------

Conceptual relationships:

``` text
locations 1 ───── * jobs
jobs      * ───── * skills
              via job_skills
```

Salary information can be absent in source postings. Missing salary
values should remain NULL/unknown, not be invented or treated as zero.

## Local setup (Windows / PowerShell)

### 1. Clone the repository

``` powershell
git clone https://github.com/YOUR_USERNAME/tech-job-analytics.git
cd tech-job-analytics
```

### 2. Create and activate a virtual environment

``` powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

``` powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file in the project root. Do not commit it.

``` env
DB_HOST=localhost
DB_PORT=3307
DB_NAME=job_analytics
DB_USER=root
DB_PASSWORD=YOUR_LOCAL_MYSQL_PASSWORD
```

From Windows, MySQL is exposed on host port `3307`. Containers on the
Compose network should connect to hostname `mysql` and internal port
`3306`. Keep the credentials in `.env`; never publish real passwords,
tokens, or API keys.

### 5. Start Docker services

``` powershell
docker compose up -d --build
docker compose ps
```

The Compose setup includes MySQL and the Airflow API server, scheduler,
DAG processor, and triggerer. It may also define an ETL service. Check
the current `docker-compose.yml` for exact service names and commands.

### 6. Run the ETL pipeline

Local Python:

``` powershell
python -m src.pipeline
```

Or, if the `etl` service is defined in your Compose file:

``` powershell
docker compose run --rm etl
```

Expected generated files (local only):

``` text
data/
├── raw/
│   └── jobs_YYYY-MM-DD.json
└── processed/
    └── jobs_cleaned.csv
```

### 7. Open Airflow

Visit <http://localhost:8080>.

The intended DAG name is `tech_job_analytics_pipeline`.

Airflow 3 health endpoint:

``` powershell
curl.exe http://127.0.0.1:8080/api/v2/monitor/health
```

## Verification commands and example outputs

The following outputs are examples of what successful checks may look
like. Exact output and CLI behavior can vary by Airflow version and
environment.

### Docker services

``` powershell
docker compose ps
```

Illustrative status:

``` text
NAME                        SERVICE                  STATUS
job-airflow-api-server      airflow-api-server       Up
job-airflow-scheduler       airflow-scheduler        Up
job-airflow-dag-processor   airflow-dag-processor    Up
job-airflow-triggerer       airflow-triggerer        Up
job-mysql                   mysql                    Up (healthy)
```

`Up` means the container is running; it does not by itself prove the
application is healthy.

### Airflow health

``` powershell
curl.exe http://127.0.0.1:8080/api/v2/monitor/health
```

Illustrative JSON:

``` json
{
  "metadatabase": {"status": "healthy"},
  "scheduler": {
    "status": "healthy",
    "latest_scheduler_heartbeat": "2026-10-18T09:00:00Z"
  },
  "triggerer": {
    "status": "healthy",
    "latest_triggerer_heartbeat": "2026-10-18T09:00:05Z"
  },
  "dag_processor": {
    "status": "healthy",
    "latest_dag_processor_heartbeat": "2026-10-18T09:00:02Z"
  }
}
```

This is a sample response, not a captured live health check. Use your
own endpoint response when documenting the current system.

### Airflow metadata database

``` powershell
docker exec job-airflow-api-server airflow db check
```

Illustrative successful output:

``` text
Connection successful.
Database check successful.
```

### Scheduler and Triggerer

``` powershell
docker exec job-airflow-scheduler airflow jobs check --job-type SchedulerJob --local
docker exec job-airflow-triggerer airflow jobs check --job-type TriggererJob --local
```

A successful check should not report a missing or stale heartbeat. CLI
output varies by Airflow version; use the health endpoint as an
additional verification.

### DAG listing

``` powershell
docker exec job-airflow-scheduler airflow dags list
```

Illustrative result:

``` text
dag_id                       | fileloc
-----------------------------|---------------------------------------
tech_job_analytics_pipeline  | /opt/airflow/dags/job_pipeline_dag.py
```

### MySQL record counts

Connect:

``` powershell
docker exec -it job-mysql mysql -u root -p job_analytics
```

Then query:

``` sql
SELECT COUNT(*) AS total_jobs FROM jobs;
SELECT COUNT(*) AS total_skills FROM skills;
SELECT COUNT(*) AS total_locations FROM locations;
SELECT COUNT(*) AS total_job_skill_links FROM job_skills;
```

Historical counts previously observed during development (not guaranteed
to be current):

  Table            Historical row count
  -------------- ----------------------
  `jobs`                             14
  `skills`                           15
  `locations`                         6
  `job_skills`                       54

Counts change as new postings are extracted and loaded. Capture fresh
query results for current project evidence.

## Power BI dashboard

Power BI is the planned final reporting layer. Connect it to the MySQL
database or to a prepared export, then build visuals such as:

-   KPI cards: total jobs, distinct skills, locations represented, and
    average salary where available.
-   Job posting trend by publication date.
-   Most frequently requested technical skills.
-   Jobs by country or location.
-   Job type distribution (only categories present in the data).
-   Salary ranges for records that actually contain salary values.

Example DAX measures (adjust names to match the actual Power BI model):

``` dax
Total Jobs = COUNTROWS(jobs)
```

``` dax
Total Skills = DISTINCTCOUNT(skills[skill_name])
```

``` dax
Average Minimum Salary = AVERAGE(jobs[salary_min])
```

For salary visuals, explain that calculations use only postings with
available salary data. Do not replace missing salaries with zero.

A dashboard mockup was generated during development to demonstrate the
intended layout. It is a design reference only, not a live Power BI
report; its displayed values are illustrative. Replace them with
measures calculated from the connected dataset before publishing.

## Testing

Run tests from the project root:

``` powershell
pytest -v
```

A previous development run reported `5 passed` with two deprecation
warnings. This is a historical result; run the tests again to report the
current status.

## GitHub safety checklist

Before committing or pushing:

-   Verify `.env` is ignored.
-   Verify `venv/`, `.pytest_cache/`, and generated data directories are
    ignored.
-   Review staged files with `git status`.
-   Never commit passwords, tokens, private keys, or confidential data.

Suggested `.gitignore` entries:

``` gitignore
.env
.env.*
!.env.example
venv/
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
data/raw/
data/processed/
airflow/logs/
*.log
```

## Future improvements

-   Add stronger data validation and schema checks.
-   Add retry handling and API rate-limit handling.
-   Maintain a versioned skill dictionary.
-   Implement incremental loading and robust duplicate handling.
-   Add structured logging and pipeline run metrics.
-   Expand automated tests for extraction, transformation, and database
    loading.
-   Complete and publish the Power BI report using real connected data.
-   Add screenshots of successful Airflow runs and the final live
    dashboard.

## Author

**Lohith Reddy B**

GitHub: [Mr-Nobody0409](https://github.com/Mr-Nobody0409)

------------------------------------------------------------------------

This project demonstrates a learning workflow for API extraction, data
transformation, relational database loading, orchestration, and
analytics reporting. Commands and configuration should be adapted to the
current repository version.
