#!/usr/bin/env python3
"""Write reviewed ``upstream.identifiers`` candidates into the rule files.

    python3 tools/apply_identifiers.py alias.json --confidence name [--dry-run]

Reads the JSON that ``gap_analysis.py --alias-candidates`` wrote, keeps the candidates of
the chosen confidence, and inserts them as text, so the rest of a rule file is untouched
(comments, key order, quoting). Each edited file is parsed again afterwards and must equal
the original document except for ``upstream.identifiers``; a file that does not is restored.
"""
import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: pip install pyyaml")


def insert(text, add):
    """*text* with the purls *add* appended to ``upstream.identifiers`` (created if absent)."""
    lines = text.splitlines(keepends=True)
    try:
        start = next(i for i, l in enumerate(lines) if re.match(r"^upstream:\s*$", l))
    except StopIteration:
        raise ValueError("no top-level 'upstream:' key")
    end = next((i for i in range(start + 1, len(lines)) if re.match(r"^\S", lines[i])), len(lines))
    purl_at = next((i for i in range(start + 1, end) if re.match(r"^\s+purl:\s", lines[i])), None)
    if purl_at is None:
        raise ValueError("no upstream.purl")
    indent = re.match(r"^(\s+)", lines[purl_at]).group(1)
    items = "".join(f"{indent}- {p}\n" for p in add)
    key_at = next((i for i in range(start + 1, end) if lines[i].rstrip() == f"{indent}identifiers:"), None)
    if key_at is None:
        lines.insert(purl_at + 1, f"{indent}identifiers:\n{items}")
    else:
        last = key_at
        while last + 1 < end and re.match(rf"^{indent}-\s", lines[last + 1]):
            last += 1
        lines.insert(last + 1, items)
    return "".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("candidates")
    ap.add_argument("--confidence", default="name", choices=["name", "review", "all"])
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    changed = failed = added = 0
    for entry in json.loads(Path(a.candidates).read_text()):
        wanted = [p["purl"] for p in entry["add"] if a.confidence in ("all", p["confidence"])]
        path = Path(entry["file"])
        original = path.read_text(encoding="utf-8")
        before = yaml.safe_load(original)
        have = set((before.get("upstream") or {}).get("identifiers") or [])
        wanted = [p for p in dict.fromkeys(wanted) if p not in have]
        if not wanted:
            continue
        try:
            text = insert(original, wanted)
            after = yaml.safe_load(text)
            expect = list((before["upstream"].get("identifiers") or [])) + wanted
            before["upstream"]["identifiers"] = expect
            if after != before:
                raise ValueError("document differs beyond upstream.identifiers")
        except (ValueError, KeyError) as exc:
            print(f"skip {path}: {exc}", file=sys.stderr)
            failed += 1
            continue
        if not a.dry_run:
            path.write_text(text, encoding="utf-8")
        changed += 1
        added += len(wanted)
    print(f"{changed} rule file(s), {added} identifier(s){' (dry run)' if a.dry_run else ''}; "
          f"{failed} skipped", file=sys.stderr)


if __name__ == "__main__":
    main()
