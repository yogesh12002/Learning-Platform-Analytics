
from pathlib import Path
import pandas as pd

# ==================================================
# 1. PROJECT PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

FILES = {
    "learners": "learners.csv",
    "courses": "courses.csv",
    "enrollments": "enrollments.csv",
    "learning_events": "learning_events.csv"
}

# ==================================================
# 2. LOAD SOURCE DATA
# ==================================================

data = {}

for name, filename in FILES.items():
    file_path = RAW_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Missing source file: {file_path}"
        )

    data[name] = pd.read_csv(file_path)

# ==================================================
# 3. SOURCE DATA PROFILE
# ==================================================

print("\n========== SOURCE DATA PROFILE ==========")

for name, df in data.items():

    print(f"\nDataset: {name}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Column names: {list(df.columns)}")
    print(f"Duplicate rows: {df.duplicated().sum()}")

    print("Null values:")
    print(df.isnull().sum().to_string())

# ==================================================
# 4. PRIMARY KEY CHECKS
# ==================================================

learners = data["learners"]
courses = data["courses"]
enrollments = data["enrollments"]
events = data["learning_events"]

print("\n========== PRIMARY KEY CHECKS ==========")

key_columns = {
    "learners": ("learner_id", learners),
    "courses": ("course_id", courses),
    "enrollments": ("enrollment_id", enrollments),
    "learning_events": ("event_id", events)
}

for name, (column, df) in key_columns.items():

    duplicate_count = df[column].duplicated().sum()

    print(
        f"{name}: duplicate {column} = "
        f"{duplicate_count}"
    )

# ==================================================
# 5. REFERENCE VALIDATION
# ==================================================

print("\n========== REFERENCE VALIDATION ==========")

unknown_enrollment_learners = (
    ~enrollments["learner_id"].isin(
        learners["learner_id"]
    )
).sum()

unknown_enrollment_courses = (
    ~enrollments["course_id"].isin(
        courses["course_id"]
    )
).sum()

unknown_event_learners = (
    ~events["learner_id"].isin(
        learners["learner_id"]
    )
).sum()

unknown_event_courses = (
    ~events["course_id"].isin(
        courses["course_id"]
    )
).sum()

print(
    "Unknown enrollment learners:",
    unknown_enrollment_learners
)

print(
    "Unknown enrollment courses:",
    unknown_enrollment_courses
)

print(
    "Unknown event learners:",
    unknown_event_learners
)

print(
    "Unknown event courses:",
    unknown_event_courses
)

# ==================================================
# 6. EVENT VALIDATION
# ==================================================

print("\n========== EVENT VALIDATION ==========")

print("\nEvent types found:")

print(
    events["event_type"]
    .value_counts()
    .to_string()
)

print(
    "\nDuplicate event IDs:",
    events["event_id"].duplicated().sum()
)

# ==================================================
# 7. EVENT DATE VALIDATION
# ==================================================

events["event_date_parsed"] = pd.to_datetime(
    events["event_date"],
    format="%d-%m-%Y",
    errors="coerce"
)

print("\n========== EVENT DATE DIAGNOSTICS ==========")

print(
    "Original data type:",
    events["event_date"].dtype
)

print("\nFirst 20 original date values:")

print(
    events["event_date"]
    .head(20)
    .to_list()
)

print("\nExamples of dates marked invalid:")

print(
    events.loc[
        events["event_date_parsed"].isna(),
        "event_date"
    ].head(20).to_list()
)

invalid_event_dates = (
    events["event_date_parsed"].isna().sum()
)

valid_event_dates = (
    events["event_date_parsed"].notna().sum()
)

print("\nInvalid event dates:", invalid_event_dates)
print("Valid event dates:", valid_event_dates)

# ==================================================
# 8. ENROLLMENT VALIDATION
# ==================================================

print("\n========== ENROLLMENT VALIDATION ==========")

print("\nEnrollment statuses:")

print(
    enrollments["enrollment_status"]
    .value_counts()
    .to_string()
)

enrollments["enrollment_date_parsed"] = pd.to_datetime(
    enrollments["enrollment_date"],
    errors="coerce"
)

invalid_enrollment_dates = (
    enrollments["enrollment_date_parsed"].isna().sum()
)

valid_enrollment_dates = (
    enrollments["enrollment_date_parsed"].notna().sum()
)

print(
    "\nInvalid enrollment dates:",
    invalid_enrollment_dates
)

print(
    "Valid enrollment dates:",
    valid_enrollment_dates
)

# ==================================================
# 9. FINAL PROFILE SUMMARY
# ==================================================

print("\n========== FINAL PROFILE SUMMARY ==========")

print("Learners:", len(learners))
print("Courses:", len(courses))
print("Enrollments:", len(enrollments))
print("Learning Events:", len(events))

print(
    "Valid Event Dates:",
    valid_event_dates
)

print(
    "Invalid Event Dates:",
    invalid_event_dates
)

print(
    "Valid Enrollment Dates:",
    valid_enrollment_dates
)

print(
    "Invalid Enrollment Dates:",
    invalid_enrollment_dates
)

print("\n========== PROFILE COMPLETED ==========")
