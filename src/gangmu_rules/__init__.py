"""The 纲目 (Gangmu) community rule base, as an installable rule pack.

gangmu finds this package through the ``gangmu.rule_packs`` entry point and
loads the directory :func:`path` returns. Nothing else lives here: the rules are
data, and every line of logic that reads them is in gangmu itself.
"""

from pathlib import Path

__version__ = "2026.10.11"


def path() -> Path:
    """The rule directory: the copy inside the wheel, or ``rules/`` in a checkout."""
    packaged = Path(__file__).resolve().parent / "data"
    if packaged.is_dir():
        return packaged
    return Path(__file__).resolve().parents[2] / "rules"
