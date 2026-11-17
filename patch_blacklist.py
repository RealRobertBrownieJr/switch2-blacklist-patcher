#!/usr/bin/env python3
"""Create a targeted blacklist-tool payload from a user's own BCAT dump.

Only removes four precisely identified launch restrictions seen in BCAT v13
on Switch 2 firmware 23.0.1. Never accesses the console or edits its files.
"""
import argparse
import copy
import json
import sys
from pathlib import Path

# (Application ID, restriction type, exact required version)
TARGETS = {
    ("0x0100c3601518c000", "SystemUpdateRequired", (23, 0, 1)): "Civilization VII: system update",
    ("0x0100c3601518c000", "ApplicationUpdateRequired", 1638400): "Civilization VII: application update",
    ("0x0100c9100b06a000", "SystemUpdateRequired", (23, 0, 1)): "SmileBASIC 4: system update",
    ("0x0100b4b00f9f6000", "SystemUpdateRequired", (23, 0, 1)): "SmileBASIC Japanese demo: system update",
}


def read_blacklist(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as e:
        raise ValueError(f"Cannot read {path}: {e}") from e
    if not isinstance(data, dict):
        raise ValueError(f"{path}: JSON root must be an object")
    if data.get("compatibility_version") != 1:
        raise ValueError(f"{path}: only compatibility_version 1 is supported")
    version = data.get("version")
    if type(version) is not int or not (0 <= version < 2**53 - 1):
        raise ValueError(f"{path}: invalid or unsupported version")
    records = data.get("records")
    if not isinstance(records, list) or not all(isinstance(r, dict) for r in records):
        raise ValueError(f"{path}: records must be an array of objects")
    return data


def fingerprint(record):
    if record.get("function_id") != "Launch":
        return None
    app_id = record.get("application_id")
    if not isinstance(app_id, str):
        return None
    kind = record.get("type")
    if kind == "SystemUpdateRequired":
        system = record.get("system")
        if not isinstance(system, dict):
            return None
        keys = ("major", "minor", "micro")
        if any(type(system.get(k)) is not int for k in keys):
            return None
        version = tuple(system[k] for k in keys)
    elif kind == "ApplicationUpdateRequired":
        app = record.get("application")
        if not isinstance(app, dict) or type(app.get("version")) is not int:
            return None
        version = app["version"]
    else:
        return None
    return (app_id.lower(), kind, version)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bcat", type=Path, help="Original BCAT blacklist dump (JSON)")
    parser.add_argument("--system", type=Path, help="Optional installed system-data blacklist dump (for version safety)")
    parser.add_argument("--output", type=Path, default=Path("payload.json"), help="Output file (default: payload.json)")
    args = parser.parse_args(argv)
    try:
        source = read_blacklist(args.bcat)
        system = read_blacklist(args.system) if args.system else None
        if args.output.exists():
            raise ValueError(f"Refusing to overwrite existing {args.output}; move/rename it first")
        if args.output.resolve() in [args.bcat.resolve()] + ([args.system.resolve()] if args.system else []):
            raise ValueError("Output must not be an original input file")
        kept, removed = [], []
        for record in source["records"]:
            key = fingerprint(record)
            if key in TARGETS:
                # Fail closed on unexpected extra fields in a matching restriction.
                expected_keys = {"application_id", "function_id", "type", "system" if key[1] == "SystemUpdateRequired" else "application"}
                version_obj = record.get("system" if key[1] == "SystemUpdateRequired" else "application")
                version_keys = {"major", "minor", "micro"} if key[1] == "SystemUpdateRequired" else {"version"}
                if set(record) != expected_keys or set(version_obj) != version_keys:
                    print(f"NOTICE: Skipped {TARGETS[key]} because this record has additional fields.")
                    kept.append(record)
                else:
                    removed.append(TARGETS[key])
            else:
                kept.append(record)
        print(f"Input: {args.bcat} (v{source['version']}, {len(source['records'])} records)")
        if system:
            print(f"System: {args.system} (v{system['version']})")
        for name in removed:
            print(f"  REMOVE: {name}")
        if not removed:
            print("No exact known restrictions found. No file written.")
            return 0
        new_version = max(source["version"], system["version"] if system else 0) + 1
        if not system:
            print("WARNING: No --system dump provided. Cannot verify version exceeds installed system blacklist.")
        result = copy.deepcopy(source)
        result["records"] = kept
        result["version"] = new_version
        # Preserve other top-level keys and record ordering, but never mutate the input.
        payload = json.dumps(result, ensure_ascii=False, indent=4) + "\n"
        assert json.loads(payload)["records"] == kept
        args.output.write_text(payload, encoding="utf-8")
        print(f"Wrote: {args.output} (v{new_version}, {len(kept)} records; removed {len(removed)})")
        print("The original input file was not modified. The console has NOT been changed.")
        return 0
    except (ValueError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
