from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import re
import subprocess

app = Flask(__name__)
CORS(app)  # Enable CORS for the HTML dashboard

TRACKING_REPO = "hackathon-tracking"


class HackathonTracker:
    def __init__(self):
        self.setup_tracking_repo()

    def setup_tracking_repo(self):
        os.makedirs("teams", exist_ok=True)
        os.makedirs("verification", exist_ok=True)
        if not os.path.exists("leaderboard.json"):
            with open("leaderboard.json", "w", encoding="utf-8") as f:
                json.dump([], f)

    # --------------------------------------------------------------
    # 1. Fetch difficulty → points from GitHub issue labels
    # --------------------------------------------------------------
    def get_bug_points(self, full_repo_name, bug_id):
        try:
            result = subprocess.run(
                [
                    "gh", "issue", "view", str(bug_id),
                    "-R", full_repo_name,
                    "--json", "labels"
                ],
                capture_output=True, text=True, check=True, timeout=10
            )
            labels = [lbl["name"].lower() for lbl in json.loads(result.stdout).get("labels", [])]

            if "difficulty-easy" in labels:
                return 5
            if "difficulty-medium" in labels:
                return 10
            if "difficulty-hard" in labels:
                return 15
            return 0
        except Exception as e:
            print(f"[ERROR] points for Bug #{bug_id}: {e}")
            return 0

    # --------------------------------------------------------------
    # 2. Log a new submission
    # --------------------------------------------------------------
    def log_bug_fix(self, team_id, bug_id, domain, commit_hash, commit_message, full_repo_name):
        team_dir = f"teams/{team_id}"
        os.makedirs(f"{team_dir}/bug-fixes", exist_ok=True)

        points = self.get_bug_points(full_repo_name, bug_id)

        submission = {
            "team_id": team_id,
            "bug_id": bug_id,
            "domain": domain,
            "commit_hash": commit_hash,
            "commit_message": commit_message,
            "submission_time": datetime.now().isoformat(),
            "status": "submitted",
            "verified": False,
            "points": points
        }

        with open(f"{team_dir}/bug-fixes/bug-{bug_id}.json", "w", encoding="utf-8") as f:
            json.dump(submission, f, indent=2)

        # ONLY update progress – leaderboard will be refreshed inside it
        self.update_progress(team_id)

        print(f"[LOG] {team_id} → Bug #{bug_id} ({points} pts)")

    # --------------------------------------------------------------
    # 3. Write progress.json **and** refresh the global leaderboard
    # --------------------------------------------------------------
    def update_progress(self, team_id):
        team_dir = f"teams/{team_id}"
        bug_files = [
            f for f in os.listdir(f"{team_dir}/bug-fixes")
            if f.endswith(".json")
        ]

        progress = {
            "team_id": team_id,
            "total_submissions": len(bug_files),
            "verified_submissions": 0,
            "total_points": 0,
            "last_submission": None,
            "submissions": [],
            "domain": "healthcare"
        }

        for bf in bug_files:
            with open(f"{team_dir}/bug-fixes/{bf}", "r", encoding="utf-8") as f:
                sub = json.load(f)
                progress["submissions"].append(sub)

                if sub["verified"]:
                    progress["verified_submissions"] += 1
                    progress["total_points"] += sub["points"]

                ts = sub["submission_time"]
                if not progress["last_submission"] or ts > progress["last_submission"]:
                    progress["last_submission"] = ts

        # write progress
        with open(f"{team_dir}/progress.json", "w", encoding="utf-8") as f:
            json.dump(progress, f, indent=2)

        # *** THIS IS THE ONLY CALL TO THE LEADERBOARD ***
        self.update_leaderboard()

    # --------------------------------------------------------------
    # 4. Re-build leaderboard.json from *all* progress files
    # --------------------------------------------------------------
    def update_leaderboard(self):
        leaderboard = []

        for td in os.listdir("teams"):
            prog_path = f"teams/{td}/progress.json"
            if not os.path.isfile(prog_path):
                continue
            with open(prog_path, "r", encoding="utf-8") as f:
                prog = json.load(f)
                leaderboard.append({
                    "team_id": prog["team_id"],
                    "bugs_solved": prog["verified_submissions"],
                    "total_points": prog["total_points"],
                    "last_submission": prog["last_submission"],
                    "domain": prog.get("domain", "healthcare")
                })

        # sort: points ↓, then earliest submission ↑
        leaderboard.sort(key=lambda x: (-x["total_points"], x["last_submission"] or ""))

        for i, entry in enumerate(leaderboard, 1):
            entry["rank"] = i

        with open("leaderboard.json", "w", encoding="utf-8") as f:
            json.dump(leaderboard, f, indent=2)

        print(f"[LEADERBOARD] {len(leaderboard)} team(s) → leaderboard.json refreshed")


tracker = HackathonTracker()


# ------------------------------------------------------------------
# Webhook entry point
# ------------------------------------------------------------------
@app.route('/webhook/github', methods=['POST'])
def handle_github_webhook():
    if request.headers.get('X-GitHub-Event') != 'push':
        return jsonify({"status": "ignored"}), 200

    repo_name = request.json['repository']['name']
    full_repo_name = request.json['repository']['full_name']

    if not repo_name.startswith('team-'):
        return jsonify({"status": "ignored"}), 200

    team_id = repo_name.split('-')[1]
    domain = repo_name.split('-')[2]

    for commit in request.json['commits']:
        bug_id = extract_bug_id(commit['message'])
        if bug_id:
            tracker.log_bug_fix(
                team_id, bug_id, domain,
                commit['id'], commit['message'],
                full_repo_name
            )

    return jsonify({"status": "processed"}), 200


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------
@app.route('/leaderboard')
def get_leaderboard():
    try:
        with open('leaderboard.json', 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except Exception:
        return jsonify([])


@app.route('/team/<team_id>')
def get_team_progress(team_id):
    path = f"teams/{team_id}/progress.json"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify({"error": "Team not found"}), 404


def extract_bug_id(message):
    patterns = [r'bug[#\s]*(\d+)', r'fix[#\s]*(\d+)', r'#(\d+)']
    for p in patterns:
        m = re.search(p, message, re.IGNORECASE)
        if m:
            return int(m.group(1))
    return None


if __name__ == '__main__':
    print("Starting Hackathon Tracker Server...")
    print("Leaderboard: http://localhost:5000/leaderboard")
    print("HTML Dashboard: open leaderboard.html")
    app.run(host='0.0.0.0', port=5000, debug=True)