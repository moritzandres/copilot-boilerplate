import json
import subprocess
import os
import sys
import re
import shutil
import hashlib
import plistlib
from pathlib import Path

WORKSPACE_DIR = os.path.abspath(os.getcwd())
JSON_FILE = ".heartbeats.json"

# Create a unique prefix based on workspace to avoid collisions
DIR_HASH = hashlib.md5(WORKSPACE_DIR.encode('utf-8')).hexdigest()[:8]
LAUNCHD_PREFIX = f"com.copilot.hb.{DIR_HASH}"
LAUNCH_AGENTS_DIR = Path.home() / "Library" / "LaunchAgents"

def validate_heartbeats(data):
    """Validates the structure and values of the parsed JSON data."""
    if not isinstance(data, dict) or "heartbeats" not in data:
        raise ValueError("Missing root 'heartbeats' key.")
    
    seen_names = set()
    for i, hb in enumerate(data.get("heartbeats", [])):
        for field in ["name", "schedule", "prompt"]:
            if field not in hb or not str(hb[field]).strip():
                raise ValueError(f"Heartbeat {i} missing/empty field: '{field}'.")

        name = hb["name"]
        if not re.match(r'^[\w-]+$', name):
            raise ValueError(f"Invalid name '{name}'. Use A-Z, a-z, 0-9, -, _.")
        if name in seen_names:
            raise ValueError(f"Duplicate heartbeat name: '{name}'.")
        seen_names.add(name)

        if len(hb["schedule"].split()) != 5:
            raise ValueError(f"Invalid cron schedule in '{name}'. Expected 5 fields.")

def parse_cron_field(field_str):
    """Converts a cron field ('*', '3', '1-5') into a list of integers, or [None] if '*'."""
    if field_str == '*':
        return [None]
    
    parts = []
    for part in field_str.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            parts.extend(range(start, end + 1))
        else:
            parts.append(int(part))
    return parts

def convert_cron_to_launchd(cron_str):
    """Converts a cron string into an array of StartCalendarInterval dictionaries."""
    minute, hour, dom, month, dow = cron_str.split()
    
    intervals = []
    # Generate the cartesian product of all time constraints
    for m in parse_cron_field(minute):
        for h in parse_cron_field(hour):
            for d in parse_cron_field(dom):
                for mo in parse_cron_field(month):
                    for dw in parse_cron_field(dow):
                        interval = {}
                        if m is not None: interval['Minute'] = m
                        if h is not None: interval['Hour'] = h
                        if d is not None: interval['Day'] = d
                        if mo is not None: interval['Month'] = mo
                        if dw is not None: interval['Weekday'] = dw
                        intervals.append(interval)
    return intervals

def clear_existing_tasks():
    """Unloads and deletes existing LaunchAgents for this workspace."""
    LAUNCH_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    
    for plist_file in LAUNCH_AGENTS_DIR.glob(f"{LAUNCHD_PREFIX}.*.plist"):
        # Unload from launchd
        subprocess.run(['launchctl', 'unload', str(plist_file)], stderr=subprocess.DEVNULL)
        # Delete file
        plist_file.unlink()

def main():
    if not os.path.exists(JSON_FILE):
        print(f"Skipping sync: {JSON_FILE} not found.")
        sys.exit(0)

    try:
        with open(JSON_FILE, 'r') as f:
            data = json.load(f)
        validate_heartbeats(data)
    except Exception as e:
        print(f"Error in {JSON_FILE}: {e}", file=sys.stderr)
        sys.exit(1)

    clear_existing_tasks()

    copilot_bin = shutil.which("copilot") or "/usr/local/bin/copilot"
    success_count = 0

    for hb in data.get("heartbeats", []):
        name = hb["name"]
        schedule = hb["schedule"]
        prompt = hb["prompt"]
        
        plist_name = f"{LAUNCHD_PREFIX}.{name}"
        plist_path = LAUNCH_AGENTS_DIR / f"{plist_name}.plist"
        
        # Build the wrapper script command
        bash_command = f'cd "{WORKSPACE_DIR}" && {copilot_bin} -p "{prompt}" --autopilot --allow-all-tools >> .copilot-{name}.log 2>&1'
        
        # Construct the Launchd Property List dictionary
        plist_dict = {
            "Label": plist_name,
            "ProgramArguments": ["/bin/bash", "-c", bash_command],
            "StartCalendarInterval": convert_cron_to_launchd(schedule),
            "RunAtLoad": False,
            "WorkingDirectory": WORKSPACE_DIR
        }

        # Write to file and load
        try:
            with open(plist_path, 'wb') as fp:
                plistlib.dump(plist_dict, fp)
            
            subprocess.run(['launchctl', 'load', str(plist_path)], check=True)
            success_count += 1
        except Exception as e:
            print(f"Failed to load launch agent '{name}': {e}", file=sys.stderr)

    print(f"Successfully synced {success_count} validated heartbeats to macOS launchd.")

if __name__ == "__main__":
    main()