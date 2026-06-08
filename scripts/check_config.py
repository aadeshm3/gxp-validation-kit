"""
check_config.py — validate workbench.config.yaml and report friendly errors.

A non-technical user edits workbench.config.yaml by hand. This script checks it
for common mistakes and prints plain-language messages with the field name and
what to fix. It never raises; it prints findings and exits 0 so it is safe to
run any time. Run it after editing the config:

    python scripts/check_config.py
"""

import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

CONFIG_FILE = Path(__file__).resolve().parent.parent / "workbench.config.yaml"


def main():
    if not CONFIG_FILE.is_file():
        print("No workbench.config.yaml found. That is fine — the framework uses "
              "safe defaults. Create one only if you want to customize it.")
        return

    try:
        import yaml
    except ImportError:
        print("PyYAML is not installed, so the config cannot be checked here. "
              "Install it with: pip install -r scripts/requirements.txt")
        return

    try:
        data = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception as exc:
        print("The config file has a formatting error and could not be read:")
        print("  {}".format(exc))
        print("Tip: check that indentation uses spaces, not tabs, and that every "
              "list item starts with '- '.")
        return

    if data is None:
        print("The config file is empty. The framework will use safe defaults.")
        return

    findings = []

    if not isinstance(data, dict):
        print("The config file should be a set of named settings. Please compare it "
              "to the original workbench.config.yaml layout.")
        return

    coverage = data.get("coverage_target_percent", 100)
    if not isinstance(coverage, (int, float)) or not (0 <= coverage <= 100):
        findings.append("coverage_target_percent must be a number from 0 to 100 "
                        "(0 turns coverage checking off). Found: {!r}".format(coverage))

    deliverables = data.get("deliverables")
    if deliverables not in (None, []) and isinstance(deliverables, list):
        for i, entry in enumerate(deliverables, 1):
            if not isinstance(entry, dict) or "template" not in entry:
                findings.append("deliverables entry #{} should list a 'template:' "
                                "and an 'alias:'. Found: {!r}".format(i, entry))

    rules = data.get("language_rules")
    if rules is not None and not isinstance(rules, dict):
        findings.append("language_rules should be a group of settings (require_terms, "
                        "flag_weak_terms, and so on), not a single value.")

    naming = data.get("naming")
    if isinstance(naming, dict):
        pattern = naming.get("draft_pattern", "")
        for token in ("{system}", "{doc}"):
            if pattern and token not in pattern:
                findings.append("naming.draft_pattern is missing {}. File names may "
                                "collide without it.".format(token))

    if findings:
        print("Found {} thing(s) to fix in workbench.config.yaml:".format(len(findings)))
        for item in findings:
            print("  - " + item)
    else:
        print("workbench.config.yaml looks good. No problems found.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("Could not check the config: {}".format(exc))
    sys.exit(0)
