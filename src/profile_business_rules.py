
from pathlib import Path
import pandas as pd

# ==================================================
# 1. PROJECT PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

# ==================================================
# 2. LOAD SOURCE DATA
# ==================================================

learners = pd.read_csv(RAW_DIR / "learners.csv")
courses = pd.read_csv(RAW_DIR / "courses.csv")
enrollments = pd.read_csv(RAW_DIR / "enrollments.csv")
events = pd.read_csv(RAW_DIR / "learning_events.csv")

datasets = {
    "learners": learners,
    "courses": courses,
    "enrollments": enrollments,
    "learning_events": events
}

# ==================================================
# 3. DISTINCT CATEGORY VALUE CHECKS
# ==================================================

print("\n========== DISTINCT CATEGORY VALUES ==========")

category_columns = {
    "learners": ["experience_level"],
    "courses": ["category"],
    "enrollments": ["enrollment_status"],
    "learning_events": ["event_type"]
}

for dataset_name, columns in category_columns.items():

    df = datasets[dataset_name]

    print(f"\nDataset: {dataset_name}")

    for column in columns:

        print(f"\nColumn: {column}")

        print(
            df[column]
            .value_counts(dropna=False)
            .to_string()
        )

# ==================================================
# 4. WHITESPACE VALIDATION
# ==================================================

print("\n========== WHITESPACE VALIDATION ==========")

for dataset_name, df in datasets.items():

    print(f"\nDataset: {dataset_name}")

    text_columns = df.select_dtypes(
        include=["object", "str"]
    ).columns

    for column in text_columns:

        values = df[column].dropna().astype(str)

        leading_spaces = values.str.startswith(" ").sum()
        trailing_spaces = values.str.endswith(" ").sum()

        empty_strings = (
            values.str.strip().eq("").sum()
        )

        print(f"\nColumn: {column}")
        print("Leading spaces:", leading_spaces)
        print("Trailing spaces:", trailing_spaces)
        print("Empty or whitespace-only strings:", empty_strings)

# ==================================================
# 5. DATE RANGE VALIDATION
# ==================================================

print("\n========== DATE RANGE VALIDATION ==========")

events["event_date_parsed"] = pd.to_datetime(
    events["event_date"],
    format="%d-%m-%Y",
    errors="coerce"
)

enrollments["enrollment_date_parsed"] = pd.to_datetime(
    enrollments["enrollment_date"],
    format="%d-%m-%Y",
    errors="coerce"
)

print("\nLearning event date range:")

print(
    "Minimum:",
    events["event_date_parsed"].min()
)

print(
    "Maximum:",
    events["event_date_parsed"].max()
)

print(
    "Invalid event dates:",
    events["event_date_parsed"].isna().sum()
)

print("\nEnrollment date range:")

print(
    "Minimum enrollment date:",
    enrollments["enrollment_date_parsed"].min()
)

print(
    "Maximum enrollment date:",
    enrollments["enrollment_date_parsed"].max()
)

print(
    "Invalid enrollment dates:",
    enrollments["enrollment_date_parsed"].isna().sum()
)

# ==================================================
# 6. ENROLLMENT RELATIONSHIP CHECKS
# ==================================================

print("\n========== ENROLLMENT RELATIONSHIP CHECKS ==========")

print(
    "Total enrollment records:",
    len(enrollments)
)

print(
    "Distinct learners enrolled:",
    enrollments["learner_id"].nunique()
)

print(
    "Distinct courses enrolled:",
    enrollments["course_id"].nunique()
)

repeated_count = enrollments.duplicated(
    subset=["learner_id", "course_id"]
).sum()

print(
    "Repeated learner-course records beyond first:",
    repeated_count
)

# ==================================================
# 7. REPEATED ENROLLMENT INVESTIGATION
# ==================================================

print("\n========== REPEATED ENROLLMENT DETAILS ==========")

repeated_combinations = enrollments[
    enrollments.duplicated(
        subset=["learner_id", "course_id"],
        keep=False
    )
].sort_values(
    ["learner_id", "course_id", "enrollment_date_parsed"]
)

if repeated_combinations.empty:

    print("No repeated learner-course combinations found.")

else:

    print(
        repeated_combinations[
            [
                "enrollment_id",
                "learner_id",
                "course_id",
                "enrollment_date",
                "enrollment_status"
            ]
        ].to_string(index=False)
    )

# ==================================================
# 8. EVENT ACTIVITY CHECKS
# ==================================================

print("\n========== EVENT ACTIVITY CHECKS ==========")

print(
    "Distinct active learners in event data:",
    events["learner_id"].nunique()
)

print(
    "Distinct courses with events:",
    events["course_id"].nunique()
)

print(
    "Distinct learner-course activity pairs:",
    events.groupby(
        ["learner_id", "course_id"]
    ).ngroups
)

# ==================================================
# 9. EVENT TYPE VALIDATION
# ==================================================

print("\n========== EVENT TYPE VALIDATION ==========")

print(
    events["event_type"]
    .value_counts()
    .to_string()
)

# ==================================================
# 10. ENROLLMENT STATUS VALIDATION
# ==================================================

print("\n========== ENROLLMENT STATUS VALIDATION ==========")

print(
    enrollments["enrollment_status"]
    .value_counts()
    .to_string()
)

# ==================================================
# 11. FINAL BUSINESS RULE SUMMARY
# ==================================================

print("\n========== FINAL BUSINESS RULE SUMMARY ==========")

print("Learners:", len(learners))
print("Courses:", len(courses))
print("Enrollments:", len(enrollments))
print("Learning Events:", len(events))

print(
    "Valid event dates:",
    events["event_date_parsed"].notna().sum()
)

print(
    "Invalid event dates:",
    events["event_date_parsed"].isna().sum()
)

print(
    "Valid enrollment dates:",
    enrollments["enrollment_date_parsed"].notna().sum()
)

print(
    "Invalid enrollment dates:",
    enrollments["enrollment_date_parsed"].isna().sum()
)

print(
    "Repeated learner-course records:",
    repeated_count
)

print("\n========== BUSINESS RULE PROFILING COMPLETED ==========")
