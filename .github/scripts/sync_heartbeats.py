import json
import os
import re
import shutil
import subprocess
import sys

WORKSPACE_DIR = os.path.abspath(os.getcwd())
JSON_FILE = ".heartbeats.json"
MARKER_START = f"# --- BEGIN COPILOT HEARTBEATS: {WORKSPACE_DIR} ---"
MARKER_END = f"# --- END COPILOT HEARTBEATS: {WORKSPACE_DIR} ---"


def validate_heartbeats(data):
    """Validates the structure and values of the parsed JSON data."""
    if not isinstance(data, dict) or "heartbeats" not in data:
        raise ValueError("Missing root 'heartbeats' key.")

    if not isinstance(data["heartbeats"], list):
        raise ValueError("'heartbeats' must be a list.")

    seen_names = set()

    for i, hb in enumerate(data["heartbeats"]):
        if not isinstance(hb, dict):
            raise ValueError(f"Item at index {i} must be a JSON object.")

        # 1. Check required fields and types
        for field in ["name", "schedule", "prompt"]:
            if field not in hb:
                raise ValueError(
                    f"Heartbeat at index {i} is missing required field: '{field}'."
                )
            if not isinstance(hb[field], str) or not hb[field].strip():
                raise ValueError(
                    f"Field '{field}' in heartbeat index {i} must be a non-empty string."
                )

        name = hb["name"]

        # 2. Validate Name (prevent command injection & duplicates)
        if not re.match(r"^[\w-]+$", name):
            raise ValueError(
                f"Heartbeat name '{name}' is invalid. Use only A-Z, a-z, 0-9, -, and _."
            )
        if name in seen_names:
            raise ValueError(
                f"Duplicate heartbeat name found: '{name}'. Names must be unique."
            )
        seen_names.add(name)

        # 3. Validate Cron Schedule Structure (basic 5-part check)
        schedule_parts = hb["schedule"].split()
        if len(schedule_parts) != 5:
            raise ValueError(
                f"Heartbeat '{name}' has an invalid cron schedule: '{hb['schedule']}'. Expected 5 space-separated fields."
            )


def get_current_crontab():
    try:
        # Fetch existing crontab
        result = subprocess.check_output(
            ["crontab", "-l"], text=True, stderr=subprocess.DEVNULL
        )
        return result.splitlines()
    except subprocess.CalledProcessError:
        # No crontab exists for this user yet
        return []


def main():
    if not os.path.exists(JSON_FILE):
        print(f"Error: {JSON_FILE} not found.")
        sys.exit(1)

    with open(JSON_FILE, "r") as f:
        data = json.load(f)

    # Validate Structure
    try:
        validate_heartbeats(data)
    except ValueError as e:
        print(f"Validation Error in {JSON_FILE}: {e}", file=sys.stderr)
        sys.exit(1)

    current_crontab = get_current_crontab()
    cleaned_crontab = []
    in_managed_block = False

    # 1. Strip out the existing heartbeat block for this specific workspace
    for line in current_crontab:
        if line == MARKER_START:
            in_managed_block = True
        elif line == MARKER_END:
            in_managed_block = False
            continue
        elif not in_managed_block:
            cleaned_crontab.append(line)

    # 2. Generate the new heartbeat block
    new_blocks = [MARKER_START]

    # Path to copilot CLI (you may need to hardcode this if cron's PATH is limited, e.g., /usr/local/bin/copilot)
    copilot_bin = shutil.which("copilot") or "/usr/local/bin/copilot"

    for hb in data.get("heartbeats", []):
        # TODO - validate the heartbeat structure and values
        # TODO - leave untouched if the heartbeat already exists and is unchanged (compare with existing block)
        name = hb["name"]
        schedule = hb["schedule"]
        prompt = hb["prompt"]

        # The command navigates to the workspace and runs the agent headlessly
        command = f'cd {WORKSPACE_DIR} && {copilot_bin} -p "{prompt}" --autopilot --allow-all-tools >> .copilot-{name}.log 2>&1'

        new_blocks.append(f"# Heartbeat: {name}")
        new_blocks.append(f"{schedule} {command}")

    new_blocks.append(MARKER_END)

    # 3. Apply the updated crontab
    final_crontab = "\n".join(cleaned_crontab + new_blocks) + "\n"

    proc = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE)
    proc.communicate(input=final_crontab.encode("utf-8"))

    print(
        f"Successfully synced {len(data.get('heartbeats', []))} heartbeats to crontab."
    )


if __name__ == "__main__":
    main()
