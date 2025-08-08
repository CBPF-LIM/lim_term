"""
Language file validator for limterm project.
Validates that all language files have the same key structure as en.yml.
"""

import os
import sys
import yaml
from pathlib import Path


class LanguageValidator:
    def __init__(self, languages_dir):
        self.languages_dir = Path(languages_dir)
        self.en_file = self.languages_dir / "en.yml"
        self.errors_found = False

    def load_yaml(self, file_path):
        """Load YAML file and return its content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None

    def get_keys_recursive(self, data, prefix=""):
        """Recursively extract all keys from a nested dictionary."""
        keys = set()

        if isinstance(data, dict):
            for key, value in data.items():
                current_key = f"{prefix}.{key}" if prefix else key
                keys.add(current_key)

                if isinstance(value, dict):
                    keys.update(self.get_keys_recursive(value, current_key))

        return keys

    def validate_language_file(self, lang_file, en_keys):
        """Validate a single language file against English keys."""
        print(f"\n--- Validating {lang_file.name} ---")

        lang_data = self.load_yaml(lang_file)
        if lang_data is None:
            self.errors_found = True
            return False

        lang_keys = self.get_keys_recursive(lang_data)

        # Find missing keys
        missing_keys = en_keys - lang_keys
        if missing_keys:
            print(f"❌ Missing keys in {lang_file.name}:")
            for key in sorted(missing_keys):
                print(f"   - {key}")
            self.errors_found = True

        # Find extra keys
        extra_keys = lang_keys - en_keys
        if extra_keys:
            print(f"❌ Extra keys in {lang_file.name}:")
            for key in sorted(extra_keys):
                print(f"   + {key}")
            self.errors_found = True

        if not missing_keys and not extra_keys:
            print(f"✅ {lang_file.name} is valid")
            return True

        return False

    def validate_line_counts(self):
        """Validate that all language files have the same number of lines."""
        print(f"\n--- Validating Line Counts ---")

        # Get all language files including en.yml
        lang_files = list(self.languages_dir.glob("*.yml"))

        if not lang_files:
            print("❌ No language files found!")
            self.errors_found = True
            return False

        # Count lines in each file
        counts = {}
        for file_path in sorted(lang_files):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    count = sum(1 for _ in f)
                counts[file_path.name] = count
                print(f"📄 {file_path.name}: {count} lines")
            except Exception as e:
                print(f"❌ Error reading {file_path.name}: {e}")
                self.errors_found = True
                return False

        # Check if all counts are the same
        unique_counts = set(counts.values())
        if len(unique_counts) != 1:
            print(f"❌ Line count mismatch! Files have different line counts: {sorted(unique_counts)}")
            self.errors_found = True
            return False
        else:
            print(f"✅ All language files have the same line count: {list(unique_counts)[0]}")
            return True

    def validate_all(self):
        """Validate all language files."""
        print("🔍 Language File Validator")
        print("=" * 50)

        # Load English reference
        if not self.en_file.exists():
            print(f"❌ Reference file {self.en_file} not found!")
            return False

        en_data = self.load_yaml(self.en_file)
        if en_data is None:
            print("❌ Failed to load English reference file!")
            return False

        en_keys = self.get_keys_recursive(en_data)
        print(f"📋 English reference has {len(en_keys)} keys")

        # Find all language files
        lang_files = [f for f in self.languages_dir.glob("*.yml") if f.name != "en.yml"]

        if not lang_files:
            print("❌ No language files found to validate!")
            return False

        print(f"🌐 Found {len(lang_files)} language files to validate")

        # Validate each file
        for lang_file in sorted(lang_files):
            self.validate_language_file(lang_file, en_keys)

        # Validate line counts
        self.validate_line_counts()

        # Summary
        print("\n" + "=" * 50)
        if self.errors_found:
            print("❌ Validation FAILED - Fix the issues above")
            return False
        else:
            print("✅ All language files are valid!")
            return True


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_languages.py <languages_directory>")
        sys.exit(1)

    languages_dir = sys.argv[1]

    if not os.path.exists(languages_dir):
        print(f"Error: Directory {languages_dir} does not exist!")
        sys.exit(1)

    validator = LanguageValidator(languages_dir)
    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
