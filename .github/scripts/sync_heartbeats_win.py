import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = SCRIPT_DIR.parent.parent
JSON_FILE = WORKSPACE_DIR / ".github" / ".heartbeats.json"

# Create a safe, unique prefix for Windows tasks based on the workspace path
# This prevents collisions between different projects.
DIR_HASH = hashlib.md5(str(WORKSPACE_DIR).encode("utf-8")).hexdigest()[:8]
TASK_PREFIX = f"CopilotHB_{DIR_HASH}_"
RUNTIME_DIR = (
    Path(os.environ.get("LOCALAPPDATA", str(WORKSPACE_DIR / ".github")))
    / "GitHubCopilotHeartbeats"
    / DIR_HASH
)


def shell_quote(value):
    return value.replace("'", "''")


def write_task_script(copilot_bin, prompt, name):
    log_name = f".copilot-{name}.log"
    workspace = shell_quote(str(WORKSPACE_DIR))
    copilot = shell_quote(copilot_bin)
    prompt_text = shell_quote(prompt)
    log_path = shell_quote(log_name)

    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    script_path = RUNTIME_DIR / f"{name}.ps1"
    script_content = (
        f"Set-Location -LiteralPath '{workspace}'\n"
        f"& '{copilot}' -p '{prompt_text}' --autopilot --allow-all-tools *>> '{log_path}'\n"
    )
    script_path.write_text(script_content, encoding="utf-8")

    return script_path


def build_task_command(script_path):
    return [
        "pwsh.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script_path),
    ]


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

        if not re.match(r"^[\w-]+$", name):
            raise ValueError(
                f"Heartbeat name '{name}' is invalid. Use only A-Z, a-z, 0-9, -, and _."
            )
        if name in seen_names:
            raise ValueError(f"Duplicate heartbeat name found: '{name}'.")
        seen_names.add(name)

        schedule_parts = hb["schedule"].split()
        if len(schedule_parts) != 5:
            raise ValueError(
                f"Heartbeat '{name}' has an invalid cron schedule. Expected 5 space-separated fields."
            )


def convert_cron_to_schtasks(cron_str, name):
    """
    Translates basic cron expressions to Windows schtasks flags.
    Supports basic daily and weekly patterns (e.g., '0 3 * * 0' or '0 18 * * 1-5').
    """
    parts = cron_str.split()
    minute, hour, dom, month, dow = parts

    args = []

    if hour == "*" or minute == "*":
        raise ValueError(
            f"Task '{name}' uses '*' for hour/minute. This script requires exact times for Windows translation."
        )

    time_str = f"{int(hour):02d}:{int(minute):02d}"

    if dom == "*" and month == "*":
        if dow == "*":
            # Daily task
            args.extend(["/SC", "DAILY", "/ST", time_str])
        else:
            # Weekly task with specific days
            dow_map = {
                "0": "SUN",
                "1": "MON",
                "2": "TUE",
                "3": "WED",
                "4": "THU",
                "5": "FRI",
                "6": "SAT",
                "7": "SUN",
            }
            days = []
            for part in dow.split(","):
                if "-" in part:
                    start, end = part.split("-")
                    try:
                        days.extend(
                            [dow_map[str(d)] for d in range(int(start), int(end) + 1)]
                        )
                    except KeyError:
                        raise ValueError(f"Invalid day range in task '{name}'.")
                elif part in dow_map:
                    days.append(dow_map[part])

            if days:
                args.extend(["/SC", "WEEKLY", "/D", ",".join(days), "/ST", time_str])
            else:
                raise ValueError(f"Failed to parse days of week for task '{name}'.")
    else:
        raise ValueError(
            f"Task '{name}' uses Month/Day-of-Month features not supported by this basic Windows translator."
        )

    return args


def clear_existing_tasks():
    """Finds and deletes all existing scheduled tasks for this specific workspace."""
    try:
        # Query all tasks in CSV format
        output = subprocess.check_output(
            ["schtasks", "/Query", "/FO", "CSV"],
            text=True,
            encoding="utf-8",
            errors="replace",
            stderr=subprocess.DEVNULL,
        )
        for line in output.splitlines():
            if TASK_PREFIX in line:
                # Extract task name (first column, strip quotes and leading slash)
                task_name = line.split(",")[0].strip('"').lstrip("\\")
                subprocess.run(
                    ["schtasks", "/Delete", "/TN", task_name, "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
    except subprocess.CalledProcessError:
        pass  # Expected if no tasks exist yet

    if RUNTIME_DIR.exists():
        shutil.rmtree(RUNTIME_DIR)


def main():
    if not JSON_FILE.exists():
        print(f"Skipping sync: {JSON_FILE} not found.")
        sys.exit(0)

    try:
        with JSON_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: {JSON_FILE} is not valid JSON. ({e})", file=sys.stderr)
        sys.exit(1)

    try:
        validate_heartbeats(data)
    except ValueError as e:
        print(f"Validation Error in {JSON_FILE}: {e}", file=sys.stderr)
        sys.exit(1)

    # 1. Purge old tasks for this workspace
    clear_existing_tasks()

    copilot_bin = shutil.which("copilot") or "copilot"
    success_count = 0

    # 2. Create new tasks
    for hb in data.get("heartbeats", []):
        name = hb["name"]
        schedule = hb["schedule"]
        prompt = hb["prompt"]

        full_task_name = f"{TASK_PREFIX}{name}"

        try:
            schtasks_args = convert_cron_to_schtasks(schedule, name)
        except ValueError as e:
            print(f"Cron Translation Error: {e}", file=sys.stderr)
            continue

        script_path = write_task_script(copilot_bin, prompt, name)
        task_run = subprocess.list2cmdline(build_task_command(script_path))

        cmd = [
            "schtasks",
            "/Create",
            "/TN",
            full_task_name,
            "/TR",
            task_run,
            "/F",
        ] + schtasks_args

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if result.returncode == 0:
            success_count += 1
        else:
            print(
                f"Failed to create task '{name}': {result.stderr.strip()}",
                file=sys.stderr,
            )

    print(
        f"Successfully synced {success_count} validated heartbeats to Windows Task Scheduler."
    )


if __name__ == "__main__":
    main()
