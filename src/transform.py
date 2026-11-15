import json
import re
from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup


SKILL_DICTIONARY = {
    "programming": {
        "python", "java", "javascript", "typescript", "c++", "c#", "golang",  "ruby"
    },

    "database": {
        "sql", "mysql", "postgresql", "mongodb", "redis"
    },

    "data_engineering": {
        "pandas", "spark", "hadoop", "airflow", "kafka", "etl", "data pipeline", "dbt"
    },

    "cloud_devops": {
        "aws", "azure", "gcp", "docker", "kubernetes"
    },

    "machine_learning": {
        "tensorflow", "pytorch", "scikit-learn", "machine learning"
    }
}


ALL_SKILLS = set()

for skills in SKILL_DICTIONARY.values():
    ALL_SKILLS.update(skills)

def load_raw_data(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return pd.DataFrame(data["jobs"])

def clean_description(description):

    if not description:
        return ""

    soup = BeautifulSoup(
        description,
        "html.parser"
    )

    text = soup.get_text(separator=" ")

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()

def normalize_title(title):

    if not title:
        return "unknown"

    title = title.lower().strip()

    return title


# -------------------------
# EXTRACT SKILLS
# -------------------------

def extract_skills(description):

    description = description.lower()

    found_skills = set()

    for skill in ALL_SKILLS:

        pattern = (
            r"(?<!\w)"
            + re.escape(skill)
            + r"(?!\w)"
        )

        if re.search(pattern, description):
            found_skills.add(skill)

    return sorted(found_skills)


# -------------------------
# PARSE SALARY
# -------------------------

def parse_salary(salary):

    if pd.isna(salary) or not salary:
        return None, None

    salary = str(salary).lower()

    numbers = re.findall(
        r"\d+(?:,\d+)?(?:\.\d+)?k?",
        salary
    )

    if not numbers:
        return None, None

    parsed_numbers = []

    for number in numbers:

        number = number.replace(",", "")

        if number.endswith("k"):
            value = float(number[:-1]) * 1000
        else:
            value = float(number)

        parsed_numbers.append(value)

    if len(parsed_numbers) == 1:
        return parsed_numbers[0], parsed_numbers[0]

    return parsed_numbers[0], parsed_numbers[1]

def transform_jobs(df):

    # Select required columns
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

    df = df[columns].copy()

    # Rename columns
    df.rename(
        columns={
            "id": "source_job_id",
            "company_name": "company",
            "candidate_required_location": "location",
            "publication_date": "published_at"
        },
        inplace=True
    )

    # Clean strings
    df["title"] = df["title"].apply(normalize_title)

    df["description"] = (
        df["description"]
        .apply(clean_description)
    )

    # Extract skills
    df["skills"] = (
        df["description"]
        .apply(extract_skills)
    )

    # Salary parsing
    salary_values = (
        df["salary"]
        .apply(parse_salary)
    )

    df[
        ["salary_min", "salary_max"]
    ] = pd.DataFrame(
        salary_values.tolist(),
        index=df.index
    )

    # Convert date
    df["published_at"] = pd.to_datetime(
        df["published_at"],
        errors="coerce"
    )

    # Remove duplicates
    df = df.drop_duplicates(
        subset=["source_job_id"]
    )

    return df

def main(input_file):

    df = load_raw_data(input_file)

    transformed_df = transform_jobs(df)

    output_directory = Path(
        "data/processed"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_directory /
        "jobs_cleaned.csv"
    )

    transformed_df.to_csv(
        output_file,
        index=False
    )

    print(
        f"Processed data saved: {output_file}"
    )

    return output_file

if __name__ == "__main__":

    raw_folder = Path("data/raw")

    latest_file = max(
        raw_folder.glob("*.json"),
        key=lambda file: file.stat().st_mtime
    )

    main(latest_file)