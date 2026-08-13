from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pydedup.scan import find_duplicates


def _render(report: dict) -> str:
    lines = ["# pydedup report", "", f"minLines: {report['minLines']}", ""]
    current_hash = None
    current = []
    for entry in report["duplicateBlocks"]:
        if entry["hash"] != current_hash:
            if current:
                lines.append(f"- `{current_hash}`:")
                for item in current:
                    lines.append(f"  - {item['path']}:{item['start']}-{item['end']}")
            current = [
                entry,
            ]
            current_hash = entry["hash"]
            continue
        current.append(entry)
    if current:
        lines.append(f"- `{current_hash}`:")
        for item in current:
            lines.append(f"  - {item['path']}:{item['start']}-{item['end']}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pydedup")
    parser.add_argument("root", type=Path)
    parser.add_argument("--min-lines", type=int, default=6)
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args(argv)

    if not args.root.exists() or not args.root.is_dir():
        print(f"Error: root does not exist or is not a directory: {args.root}", file=sys.stderr)
        return 1

    report = find_duplicates(args.root, min_lines=args.min_lines).as_dict()
    print(_render(report))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
