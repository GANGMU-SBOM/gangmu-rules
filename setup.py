"""Build hook: copy the top-level ``rules/`` tree into the wheel.

Contributors edit ``rules/``; at build time it becomes ``gangmu_rules/data`` so
``pip install gangmu-rules`` carries the whole rule base.
"""

import hashlib
import json
import shutil
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py


INDEX_NAME = ".rule-index.json"
INDEX_FORMAT = 1


def write_rule_index(root: Path) -> int:
    """Precompile the rule YAML so gangmu loads it without parsing YAML.

    This writes the file `gangmu rules index` writes (format 1: for each rule
    file its sha256 and its parse). gangmu uses an entry only when the hash of
    the file it finds matches, so the index can only ever save time. A file
    whose parse does not survive JSON unchanged (an unquoted date) is left out.
    CI builds the index with gangmu itself and compares the two.
    """
    import yaml

    files = {}
    for path in sorted(root.rglob("*.y*ml")):
        if path.name.startswith("."):
            continue
        data = path.read_bytes()
        raw = yaml.safe_load(data.decode("utf-8"))
        try:
            if raw is None or json.loads(json.dumps(raw)) != raw:
                continue
        except (TypeError, ValueError):
            continue
        files[path.relative_to(root).as_posix()] = {
            "sha256": hashlib.sha256(data).hexdigest(), "raw": raw}
    (root / INDEX_NAME).write_text(
        json.dumps({"format": INDEX_FORMAT, "files": files},
                   sort_keys=True, separators=(",", ":")), encoding="utf-8")
    return len(files)


class BuildPyWithRules(build_py):
    def run(self):
        super().run()
        src = Path(__file__).parent / "rules"
        if not (src / "rulebase.json").is_file():
            raise SystemExit("rules/rulebase.json not found; refusing to build an empty rule pack")
        dest = Path(self.build_lib) / "gangmu_rules" / "data"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__"))
        write_rule_index(dest)


setup(cmdclass={"build_py": BuildPyWithRules})
