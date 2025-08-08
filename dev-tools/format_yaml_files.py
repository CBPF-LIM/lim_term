"""
YAML formatter to ensure all language files have consistent formatting and line counts.
"""

import yaml
from pathlib import Path


def standardize_yaml_format(file_path):
    """Standardize YAML file formatting."""
    print(f"Formatting {file_path.name}...")

    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(
            data,
            f,
            default_flow_style=False,
            allow_unicode=True,
            indent=2,
            sort_keys=False,
            width=1000,
            explicit_end=False,
            explicit_start=False,
        )

    with open(file_path, "r", encoding="utf-8") as f:
        line_count = sum(1 for _ in f)

    print(f"✅ Formatted {file_path.name} - {line_count} lines")
    return line_count


def main():
    languages_dir = Path("limterm/languages")

    for yaml_file in sorted(languages_dir.glob("*.yml")):
        standardize_yaml_format(yaml_file)

    print("✅ All YAML files have been standardized!")


if __name__ == "__main__":
    main()
