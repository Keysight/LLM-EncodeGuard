"""
Analyze NO_LEAK_DETECTED results from a baseline CSV file.

Usage:
    python analyze_no_leak.py <csv_file> [--compare 1,2,3,4,...]

Example:
    python analyze_no_leak.py outputs/baseline/custom/model_baseline.csv \
        --compare "1,2,3,4,7,8,9,10,11,12,18,19,20,21,22,23,24,28,29,30"
"""

import csv
import argparse


DEFAULT_COMPARE = [
    1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 18, 19, 20, 21, 22, 23, 24,
    28, 29, 30, 33, 34, 35, 37, 39, 44, 47, 50, 53, 55, 58, 59,
    60, 62, 64, 66, 67, 70, 71, 73, 74, 75, 77, 78, 79, 80
]


def extract_indexes_by_result(csv_path: str) -> tuple[list[int], list[int]]:
    no_leak, leak = [], []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            idx = int(row["Prompt Index"].strip())
            if row.get("Attack Result", "").strip() == "NO_LEAK_DETECTED":
                no_leak.append(idx)
            else:
                leak.append(idx)
    return sorted(no_leak), sorted(leak)


def analyze(csv_path: str, compare_list: list[int]) -> None:
    no_leak, leak = extract_indexes_by_result(csv_path)
    compare_set = set(compare_list)
    no_leak_set = set(no_leak)

    common = sorted(no_leak_set & compare_set)
    missing_from_list = sorted(compare_set - no_leak_set)

    print(f"File: {csv_path}")

    print(f"\nNO_LEAK_DETECTED indexes [{len(no_leak)}]:")
    print(", ".join(map(str, no_leak)))

    print(f"\nLEAK_DETECTED indexes [{len(leak)}]:")
    print(", ".join(map(str, leak)))

    print(f"\nCommon NO_LEAK_DETECTED indexes [{len(common)}]:")
    print(", ".join(map(str, common)) if common else "  (none)")

    print(f"\nMissing NO_LEAK_DETECTED indexes from the list [{len(missing_from_list)}]:")
    print(", ".join(map(str, missing_from_list)) if missing_from_list else "  (none)")


def main():
    parser = argparse.ArgumentParser(description="Analyze NO_LEAK_DETECTED from a baseline CSV.")
    parser.add_argument("csv_file", help="Path to the baseline CSV file")
    parser.add_argument(
        "--compare",
        help="Comma-separated list of prompt indexes to compare against",
        default=None,
    )
    args = parser.parse_args()

    if args.compare:
        compare_list = [int(x.strip()) for x in args.compare.split(",") if x.strip()]
    else:
        compare_list = DEFAULT_COMPARE

    analyze(args.csv_file, compare_list)


if __name__ == "__main__":
    main()
