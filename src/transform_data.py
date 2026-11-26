
from pathlib import Path
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
REJECTED_DIR = BASE_DIR / "data" / "rejected"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REJECTED_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# DATASET CONFIGURATION
# ============================================================

DATASETS = {
    "learners": {
        "file": "learners.csv",
        "primary_key": "learner_id",
        "required": [
            "learner_id",
            "learner_name",
            "experience_level"
        ],
        "date_columns": {}
    },
    "courses": {
        "file": "courses.csv",
        "primary_key": "course_id",
        "required": [
            "course_id",
            "course_name",
            "category"
        ],
        "date_columns": {}
    },
    "enrollments": {
        "file": "enrollments.csv",
        "primary_key": "enrollment_id",
        "required": [
            "enrollment_id",
            "learner_id",
            "course_id",
            "enrollment_date",
            "enrollment_status"
        ],
        "date_columns": {
            "enrollment_date": "%d-%m-%Y"
        }
    },
    "learning_events": {
        "file": "learning_events.csv",
        "primary_key": "event_id",
        "required": [
            "event_id",
            "learner_id",
            "course_id",
            "event_date",
            "event_type"
        ],
        "date_columns": {
            "event_date": "%d-%m-%Y"
        }
    }
}


# ============================================================
# HELPER FUNCTION: LOAD DATA
# ============================================================

def load_dataset(dataset_name, config):

    file_path = RAW_DIR / config["file"]

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required source file not found: {file_path}"
        )

    df = pd.read_csv(file_path, dtype=str)

    # Remove accidental whitespace from column names
    df.columns = df.columns.str.strip()

    print(f"\nLoaded {dataset_name}: {len(df)} records")

    return df


# ============================================================
# HELPER FUNCTION: CLEAN TEXT
# ============================================================

def clean_text(df):

    for column in df.select_dtypes(include=["object", "str"]).columns:
        df[column] = df[column].str.strip()

    return df


# ============================================================
# HELPER FUNCTION: VALIDATE DATA
# ============================================================

def validate_dataset(
    dataset_name,
    df,
    config,
    valid_learner_ids,
    valid_course_ids
):

    df = df.copy()

    rejection_reasons = pd.Series(
        "",
        index=df.index,
        dtype="object"
    )

    # --------------------------------------------------------
    # 1. Required field validation
    # --------------------------------------------------------

    for column in config["required"]:

        if column not in df.columns:
            raise ValueError(
                f"{dataset_name}: Missing required column '{column}'"
            )

        invalid = (
            df[column].isna() |
            df[column].eq("")
        )

        rejection_reasons.loc[invalid] += (
            f"Missing required value: {column}; "
        )

    # --------------------------------------------------------
    # 2. Primary key validation
    # Quarantine every row sharing a duplicate primary key.
    # --------------------------------------------------------

    primary_key = config["primary_key"]

    duplicate_key = (
        df[primary_key].notna() &
        df[primary_key].ne("") &
        df[primary_key].duplicated(keep=False)
    )

    rejection_reasons.loc[duplicate_key] += (
        f"Duplicate primary key: {primary_key}; "
    )

    # --------------------------------------------------------
    # 3. Date validation
    # --------------------------------------------------------

    for column, date_format in config["date_columns"].items():

        parsed_dates = pd.to_datetime(
            df[column],
            format=date_format,
            errors="coerce"
        )

        invalid_date = (
            df[column].notna() &
            df[column].ne("") &
            parsed_dates.isna()
        )

        rejection_reasons.loc[invalid_date] += (
            f"Invalid date: {column}; "
        )

        # Normalize valid dates to YYYY-MM-DD
        valid_date = parsed_dates.notna()

        df.loc[valid_date, column] = (
            parsed_dates.loc[valid_date].dt.strftime("%Y-%m-%d")
        )

    # --------------------------------------------------------
    # 4. Foreign key validation
    # --------------------------------------------------------

    if dataset_name in ["enrollments", "learning_events"]:

        invalid_learner = (
            df["learner_id"].ne("") &
            df["learner_id"].notna() &
            ~df["learner_id"].isin(valid_learner_ids)
        )

        invalid_course = (
            df["course_id"].ne("") &
            df["course_id"].notna() &
            ~df["course_id"].isin(valid_course_ids)
        )

        rejection_reasons.loc[invalid_learner] += (
            "Unknown learner_id reference; "
        )

        rejection_reasons.loc[invalid_course] += (
            "Unknown course_id reference; "
        )

    # --------------------------------------------------------
    # 5. Separate valid and rejected records
    # --------------------------------------------------------

    rejected_mask = rejection_reasons.ne("")

    valid_df = df.loc[~rejected_mask].copy()
    rejected_df = df.loc[rejected_mask].copy()

    rejected_df["rejection_reason"] = (
        rejection_reasons.loc[rejected_mask].str.rstrip("; ")
    )

    return valid_df, rejected_df


# ============================================================
# MAIN ETL PROCESS
# ============================================================

def main():

    print("\n======================================")
    print("TEAM 8 - LEARNING PLATFORM ETL")
    print("======================================")

    raw_data = {}

    # --------------------------------------------------------
    # STEP 1: LOAD ALL DATASETS
    # --------------------------------------------------------

    for dataset_name, config in DATASETS.items():

        raw_data[dataset_name] = load_dataset(
            dataset_name,
            config
        )

        raw_data[dataset_name] = clean_text(
            raw_data[dataset_name]
        )

    # --------------------------------------------------------
    # STEP 2: BUILD MASTER REFERENCE LISTS
    # Use non-empty source IDs for referential validation.
    # --------------------------------------------------------

    valid_learner_ids = set(
        raw_data["learners"]["learner_id"].dropna()
    )

    valid_learner_ids.discard("")

    valid_course_ids = set(
        raw_data["courses"]["course_id"].dropna()
    )

    valid_course_ids.discard("")

    # --------------------------------------------------------
    # STEP 3: VALIDATE AND TRANSFORM DATASETS
    # --------------------------------------------------------

    summary = []

    for dataset_name, config in DATASETS.items():

        print(f"\nProcessing: {dataset_name}")

        valid_df, rejected_df = validate_dataset(
            dataset_name,
            raw_data[dataset_name],
            config,
            valid_learner_ids,
            valid_course_ids
        )

        # ----------------------------------------------------
        # STEP 4: SAVE CURATED DATA
        # ----------------------------------------------------

        curated_path = (
            PROCESSED_DIR /
            f"{dataset_name}_curated.csv"
        )

        valid_df.to_csv(
            curated_path,
            index=False
        )

        # ----------------------------------------------------
        # STEP 5: SAVE REJECTED DATA
        # ----------------------------------------------------

        rejected_path = (
            REJECTED_DIR /
            f"{dataset_name}_rejected.csv"
        )

        rejected_df.to_csv(
            rejected_path,
            index=False
        )

        summary.append({
            "dataset": dataset_name,
            "source_records": len(raw_data[dataset_name]),
            "curated_records": len(valid_df),
            "rejected_records": len(rejected_df)
        })

        print(f"Source records   : {len(raw_data[dataset_name])}")
        print(f"Curated records  : {len(valid_df)}")
        print(f"Rejected records : {len(rejected_df)}")

        print(f"Curated output   : {curated_path}")
        print(f"Rejected output  : {rejected_path}")

    # --------------------------------------------------------
    # STEP 6: SAVE ETL SUMMARY
    # --------------------------------------------------------

    summary_df = pd.DataFrame(summary)

    summary_path = (
        BASE_DIR /
        "reports" /
        "etl_summary.csv"
    )

    summary_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    summary_df.to_csv(
        summary_path,
        index=False
    )

    print("\n======================================")
    print("ETL PROCESS COMPLETED")
    print("======================================")

    print(summary_df.to_string(index=False))

    print(f"\nSummary report saved: {summary_path}")


if __name__ == "__main__":
    main()
