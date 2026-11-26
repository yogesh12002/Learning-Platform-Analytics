
from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
REPORT_DIR = BASE_DIR / "reports"

REPORT_DIR.mkdir(parents=True, exist_ok=True)


ALLOWED_VALUES = {
    "learners": {
        "experience_level": [
            "Beginner",
            "Intermediate",
            "Advanced"
        ]
    },
    "courses": {
        "category": [
            "Cloud",
            "Data",
            "Analytics",
            "Programming"
        ]
    },
    "enrollments": {
        "enrollment_status": [
            "ACTIVE",
            "COMPLETED",
            "DROPPED"
        ]
    },
    "learning_events": {
        "event_type": [
            "LOGIN",
            "VIDEO_PLAY",
            "QUIZ_ATTEMPT",
            "LESSON_COMPLETE"
        ]
    }
}


def validate_values(dataset_name, df, rules):

    results = []

    for column, allowed_values in rules.items():

        actual_values = set(
            df[column].dropna().astype(str).str.strip().unique()
        )

        unexpected_values = actual_values - set(allowed_values)

        missing_allowed_values = set(allowed_values) - actual_values

        results.append({
            "dataset": dataset_name,
            "column": column,
            "actual_distinct_values": len(actual_values),
            "unexpected_values": ", ".join(
                sorted(unexpected_values)
            ),
            "missing_allowed_values": ", ".join(
                sorted(missing_allowed_values)
            ),
            "validation_status": (
                "PASS" if not unexpected_values else "FAIL"
            )
        })

    return results


def main():

    all_results = []

    for dataset_name, rules in ALLOWED_VALUES.items():

        file_path = (
            PROCESSED_DIR /
            f"{dataset_name}_curated.csv"
        )

        if not file_path.exists():
            raise FileNotFoundError(
                f"Curated file missing: {file_path}"
            )

        df = pd.read_csv(file_path, dtype=str)

        print(f"\nValidating {dataset_name}")

        results = validate_values(
            dataset_name,
            df,
            rules
        )

        for result in results:

            all_results.append(result)

            print(f"Column: {result['column']}")
            print(
                f"Unexpected values: "
                f"{result['unexpected_values'] or 'None'}"
            )
            print(
                f"Missing allowed values: "
                f"{result['missing_allowed_values'] or 'None'}"
            )
            print(
                f"Status: {result['validation_status']}"
            )

    report = pd.DataFrame(all_results)

    report_path = (
        REPORT_DIR /
        "business_rule_validation.csv"
    )

    report.to_csv(report_path, index=False)

    print("\n======================================")
    print("BUSINESS RULE VALIDATION SUMMARY")
    print("======================================")

    print(report.to_string(index=False))

    if (report["validation_status"] == "FAIL").any():
        print("\nBusiness-rule validation requires investigation.")
    else:
        print("\nAll observed values passed validation.")

    print(f"\nReport saved: {report_path}")


if __name__ == "__main__":
    main()
