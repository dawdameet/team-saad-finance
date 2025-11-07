# populate_fintech_bugs_from_markdown.py
# Purpose: Automatically create GitHub issues for all Fintech bugs
# Source: detailed_bugs_ordered.md
# Behavior: Parses markdown, extracts bug data, creates labels, then creates issues
# Run with: python populate_fintech_bugs_from_markdown.py
# Prerequisites: GitHub CLI (gh) authenticated and write access to the repo.

import subprocess
import re
import json
import sys
from pathlib import Path

# =========================
# CONFIGURATION
# =========================
REPO = "Rishpal27/Arya-Tasks"  # <--- Fill in manually, e.g. "org/fintech-project"

MARKDOWN_FILE = "./detailed_bugs_ordered.md"


# =========================
# STEP 1: Create GitHub Labels
# =========================
def create_labels(repo):
    print(f"Creating labels for {repo or '[REPO NOT SET]'}...")

    labels = [
        {"name": "fintech", "color": "0366d6", "desc": "Fintech project module"},
        {"name": "puzzle", "color": "9f7ae2", "desc": "Puzzle-style bug with riddle hint"},
        {"name": "difficulty-easy", "color": "28a745", "desc": "Easy difficulty (5 pts)"},
        {"name": "difficulty-medium", "color": "ffc107", "desc": "Medium difficulty (10 pts)"},
        {"name": "difficulty-hard", "color": "dc3545", "desc": "Hard difficulty (15 pts)"},
    ]

    # Add generic bug-1 to bug-20 labels (can be extended)
    for i in range(1, 21):
        labels.append({
            "name": f"bug-{i}",
            "color": "d73a4a",
            "desc": f"Bug #{i} in Fintech project"
        })

    for label in labels:
        try:
            subprocess.run([
                "gh", "label", "create", label["name"],
                "--repo", repo,
                "--color", label["color"],
                "--description", label["desc"]
            ], check=True, capture_output=True)
            print(f"✅ Created label: {label['name']}")
        except subprocess.CalledProcessError:
            print(f"⚠️  Label {label['name']} already exists; skipping.")


# =========================
# STEP 2: Parse Markdown File
# =========================
def parse_markdown_bugs(md_path):
    text = Path(md_path).read_text(encoding="utf-8")

    # Split at "### [Bxx]" style markers
    bug_blocks = re.split(r"(?=### \[B\d+\])", text)
    bugs = []

    for block in bug_blocks:
        if not block.strip().startswith("### [B"):
            continue

        bug_id_match = re.search(r"\[B(\d+)\]", block)
        title_match = re.search(r"### \[B\d+\]\s+(.*)", block)
        type_match = re.search(r"\*\*Type:\*\*\s*(.*)", block)
        category_match = re.search(r"\*\*Category:\*\*\s*(.*)", block)
        file_match = re.search(r"\*\*File:\*\*\s*`([^`]+)`", block)
        location_match = re.search(r"\*\*Location:\*\*\s*`([^`]+)`", block)
        description_match = re.search(r"\*\*Bug Description:\*\*\n(.*?)(?=\n\*\*Root Cause:)", block, re.S)
        root_cause_match = re.search(r"\*\*Root Cause:\*\*\n(.*?)(?=\n\*\*Impact:)", block, re.S)
        impact_match = re.search(r"\*\*Impact:\*\*\n(.*?)(?=\n\*\*Expected Symptom:)", block, re.S)
        expected_symptom_match = re.search(r"\*\*Expected Symptom:\*\*\n(.*?)(?=\n\*\*Validation Criteria)", block, re.S)
        validation_match = re.search(r"\*\*Validation Criteria for Fix:\*\*\n(.*?)(?=\n\*\*Technical Details:)", block, re.S)

        bug_id = int(bug_id_match.group(1)) if bug_id_match else None
        title = title_match.group(1).strip() if title_match else "Untitled Bug"
        difficulty = (type_match.group(1).lower() if type_match else "medium").strip()
        category = category_match.group(1).strip() if category_match else ""
        file_path = file_match.group(1) if file_match else ""
        location = location_match.group(1) if location_match else ""
        description = description_match.group(1).strip() if description_match else ""
        root_cause = root_cause_match.group(1).strip() if root_cause_match else ""
        impact = impact_match.group(1).strip() if impact_match else ""
        expected = expected_symptom_match.group(1).strip() if expected_symptom_match else ""
        validation = validation_match.group(1).strip() if validation_match else ""

        # Assign point values based on difficulty
        points = {"easy": 5, "medium": 10, "hard": 15}.get(difficulty, 10)

        bugs.append({
            "id": bug_id,
            "title": title,
            "difficulty": difficulty,
            "points": points,
            "category": category,
            "file": file_path,
            "location": location,
            "description": description,
            "root_cause": root_cause,
            "impact": impact,
            "expected": expected,
            "validation": validation
        })

    print(f"🪲 Parsed {len(bugs)} bugs from markdown file.")
    return bugs


# =========================
# STEP 3: Create GitHub Issues
# =========================
def create_bug_issues(repo, bugs):
    if not repo:
        print("❌ ERROR: Repository name is blank. Please set the REPO variable.")
        sys.exit(1)

    print(f"Populating Fintech puzzle bugs into {repo}...")
    created_count = 0

    for bug in bugs:
        body = f"""
## Bug Description
{bug['description']}

## Root Cause
{bug['root_cause']}

## Impact
{bug['impact']}

## Expected Symptom
{bug['expected']}

## Validation Criteria for Fix
{bug['validation']}

## Files Affected
`{bug['file']}` — `{bug['location']}`

## Category
{bug['category']}

---
**Bug ID:** {bug['id']}
**Module:** Fintech Project
**Difficulty:** {bug['difficulty'].upper()}
**Points:** {bug['points']}
**Status:** UNRESOLVED
"""

        labels = [
            f"bug-{bug['id']}",
            "fintech",
            "puzzle",
            f"difficulty-{bug['difficulty']}"
        ]
        label_str = ",".join(labels)

        try:
            subprocess.run([
                "gh", "issue", "create",
                "-R", repo,
                "-t", f"Bug {bug['id']}: {bug['title']}",
                "-b", body,
                "--label", label_str
            ], check=True, capture_output=True)
            print(f"✅ Created issue for Bug {bug['id']}: {bug['title']}")
            created_count += 1
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create issue for Bug {bug['id']}: {e}")
            if e.stderr:
                print(f"  Error: {e.stderr.decode()}")

    print(f"🎯 Total issues created: {created_count}/{len(bugs)}")


# =========================
# MAIN EXECUTION
# =========================
if __name__ == "__main__":
    if not Path(MARKDOWN_FILE).exists():
        print(f"❌ Markdown file not found: {MARKDOWN_FILE}")
        sys.exit(1)

    bugs_data = parse_markdown_bugs(MARKDOWN_FILE)
    create_labels(REPO)
    create_bug_issues(REPO, bugs_data)
