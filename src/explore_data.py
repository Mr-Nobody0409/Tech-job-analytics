import json
from pathlib import Path
import pandas as pd

# Find the raw JSON file
file_path = Path("data/raw/jobs_2026-09-11.json")

# Load JSON into python dictionary
with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Extract jobs list
jobs = data["jobs"]

# Convert to DataFrame
df = pd.DataFrame(jobs)

# Select useful columns
columns = [
    "id",
    "title",
    "company_name",
    "candidate_required_location",
    "category",
    "job_type",
    "publication_date",
    "description",
    "salary"
]

df = df[columns]

# Rename columns
df = df.rename(
    columns={
        "id": "source_job_id",
        "company_name": "company",
        "candidate_required_location": "location",
        "publication_date": "published_at"
    }
)

# Explore data
print("\n--- DATA SHAPE ---")
print(df.shape)

print("\n--- COLUMNS ---")
print(df.columns.tolist())

print("\n--- DATA TYPES ---")
print(df.dtypes)

print("\n--- MISSING VALUES ---")
print(df.isnull().sum())

print("\n--- FIRST 5 ROWS ---")
print(
    df[
        [
            "source_job_id",
            "title",
            "company",
            "location",
            "salary"
        ]
    ].head()
)