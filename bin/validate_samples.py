import argparse
import re
import sys
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "sample_id",
    "species",
    "tissue",
    "genotype",
    "treatment",
    "read_1",
    "read_2",
}
CONTROLLED_VOCABULARY = {
    "species": {"Zea mays"},
    "tissue": {"leaf", "root"},
    "treatment": {"control", "edited"},
}


def validate(input_path: Path, output_dir: Path) -> bool:
    try:
        df = pd.read_csv(input_path, dtype=str, keep_default_na=False)
    except (OSError, pd.errors.ParserError, UnicodeError) as exc:
        print(f"Could not read {input_path}: {exc}", file=sys.stderr)
        return False

    df = df.apply(lambda column: column.str.strip())
    errors = []
    missing_columns = sorted(REQUIRED_COLUMNS - set(df.columns))

    for column in missing_columns:
        errors.append({
            "row": "",
            "sample_id": "",
            "column": column,
            "value": "",
            "problem": "Required column is missing",
        })

    row_issues = {}
    for index, row in df.iterrows():
        csv_row = index + 2  # Header is line 1.
        issues = []

        for column, allowed in CONTROLLED_VOCABULARY.items():
            value = row.get(column, "")
            if value and value not in allowed:
                issues.append((column, value, f"Must be one of: {', '.join(sorted(allowed))}"))

        sample_id = row.get("sample_id", "")
        for column, read_number in (("read_1", "R1"), ("read_2", "R2")):
            value = row.get(column, "")
            expected = (
                rf"data/fastq/{re.escape(sample_id)}_{read_number}\.fastq\.gz"
                if sample_id
                else None
            )
            if not value or not expected or not re.fullmatch(expected, value):
                issues.append((
                    column,
                    value,
                    f"Expected data/fastq/{{sample_id}}_{read_number}.fastq.gz",
                ))

        if sample_id and "sample_id" in df.columns:
            if df["sample_id"].eq(sample_id).sum() > 1:
                issues.append(("sample_id", sample_id, "Duplicate sample ID"))

        for column in REQUIRED_COLUMNS & set(df.columns):
            if not row.get(column, ""):
                issues.append((column, "", "Required value is blank"))

        if missing_columns and not issues:
            issues.append(("", "", "Cannot validate row because required columns are missing"))

        row_issues[index] = issues
        for column, value, problem in issues:
            errors.append({
                "row": csv_row,
                "sample_id": sample_id,
                "column": column,
                "value": value,
                "problem": problem,
            })

    output_dir.mkdir(parents=True, exist_ok=True)
    valid_indices = [
        index for index, issues in row_issues.items()
        if not issues and not missing_columns
    ]
    df.loc[valid_indices].to_csv(output_dir / "validated_samples.csv", index=False)
    pd.DataFrame(
        errors, columns=["row", "sample_id", "column", "value", "problem"]
    ).to_csv(output_dir / "validation_errors.csv", index=False)

    return not errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a samples CSV.")
    parser.add_argument("--input", type=Path, help="Path to the input CSV")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("."),
        help="Directory for validated_samples.csv and validation_errors.csv",
    )
    args = parser.parse_args()
    return 0 if validate(args.input, args.output) else 1


if __name__ == "__main__":
    sys.exit(main())