from extract import extract_jobs, save_raw_data
from transform import main as transform_data
from load import main as load_data


def run_pipeline():

    print("=" * 50)
    print("STARTING ETL PIPELINE")
    print("=" * 50)

    # -------------------------
    # 1. EXTRACT
    # -------------------------

    print("\n[1/3] Extracting data...")

    data = extract_jobs()

    raw_file = save_raw_data(data)

    # -------------------------
    # 2. TRANSFORM
    # -------------------------

    print("\n[2/3] Transforming data...")

    processed_file = transform_data(
        raw_file
    )

    # -------------------------
    # 3. LOAD
    # -------------------------

    print("\n[3/3] Loading data into MySQL...")

    load_data(
        processed_file
    )

    print("\n" + "=" * 50)
    print("ETL PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 50)


if __name__ == "__main__":

    run_pipeline()