#!/usr/bin/env python3
"""Reverse gap analysis: which C/C++ upstreams does OSV know vulnerabilities for,
that this rule base has no rule for yet?

Reads OSV bulk dumps (``GIT``, optionally ``Debian`` and ``Linux``), never the
network. Fetch them first:

    for e in GIT Debian; do
      curl -O https://osv-vulnerabilities.storage.googleapis.com/$e/all.zip; done
    python3 tools/gap_analysis.py --git GIT.zip --debian Debian.zip --top 300 \
        --out-md gap.md --out-json gap.json

Method
  * Every OSV record with a GIT range names an upstream repository by URL. Group
    records by repository (normalised to the purl key ``pkg:github/owner/repo``).
  * Keep repositories whose records carry Vanir signatures that point at C/C++
    files (``.c .h .cc .cpp .hpp``); that is OSV's own evidence of the language.
  * Debian records share CVE ids with the GIT records: the Debian package names
    seen on those CVEs become *distro aliases* for the upstream (the data a
    purl-alias layer would need, e.g. zlib -> pkg:deb/debian/zlib).
  * Compare with rules/**/*.yaml (``upstream.purl``, ``upstream.source.url``,
    mirrors, ``vendor_fork.upstream_of_fork``) to label each repo covered / missing.
"""
import argparse
import json
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: pip install pyyaml")

CVE_RE = re.compile(r"CVE-\d{4}-\d{4,}")
C_EXT = (".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".hh")
HOSTS = {"github.com": "github", "gitlab.com": "gitlab", "bitbucket.org": "bitbucket"}
URL_RE = re.compile(r"^(?:https?|git|ssh)://(?:[^@/]+@)?(?:www\.)?([^/:]+)(?::\d+)?/(.+?)(?:\.git)?/*$", re.I)


def repo_key(url):
    """URL -> ``pkg:github/o/r`` or ``pkg:generic/host/path`` (lower-case)."""
    m = URL_RE.match((url or "").strip())
    if not m:
        return None
    host, path = m.group(1).lower(), m.group(2).strip("/")
    kind = HOSTS.get(host)
    if kind:
        parts = path.split("/")
        if len(parts) < 2:
            return None
        return f"pkg:{kind}/{parts[0]}/{parts[1]}".lower()
    return f"pkg:generic/{host}/{path}".lower()


def purl_key(purl):
    if not purl or not purl.startswith("pkg:"):
        return None
    body = purl[4:].split("#")[0].split("?")[0]
    at = body.find("@", body.rfind("/") + 1)
    return ("pkg:" + (body[:at] if at != -1 else body)).strip("/").lower()


def load_rule_keys(rules_dir):
    """repo key -> rule id, from every identity a rule states."""
    keys = {}
    for path in sorted(Path(rules_dir).rglob("*.yaml")):
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(doc, dict) or "id" not in doc:
            continue
        up = doc.get("upstream") or {}
        src = up.get("source") or {}
        urls = [src.get("url"), (doc.get("vendor_fork") or {}).get("upstream_of_fork")]
        urls += [m.get("url") for m in up.get("mirrors") or [] if isinstance(m, dict)]
        found = [repo_key(u) for u in urls] + [purl_key(up.get("purl"))]
        for k in found:
            if k:
                keys.setdefault(k, doc["id"])
    return keys


def load_rule_meta(rules_dir):
    """rule id -> {purl, names, identifiers} for every rule that has a purl."""
    meta = {}
    for path in sorted(Path(rules_dir).rglob("*.yaml")):
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(doc, dict) or "id" not in doc:
            continue
        up = doc.get("upstream") or {}
        if up.get("purl"):
            names = {str(doc["id"]).rsplit("/", 1)[-1], (doc.get("component") or {}).get("ships_as"),
                     up.get("name"), str(up["purl"]).split("@")[0].rsplit("/", 1)[-1]}
            meta[doc["id"]] = {"purl": up["purl"], "path": str(path),
                               "names": {norm_name(n) for n in names if n},
                               "identifiers": list(up.get("identifiers") or [])}
    return meta


def norm_name(text):
    return re.sub(r"[^a-z0-9]", "", str(text or "").lower())


def load_rule_names(rules_dir):
    """normalised names a rule goes by -> rule id (id tail, ships_as, upstream.name)."""
    names = {}
    for path in sorted(Path(rules_dir).rglob("*.yaml")):
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(doc, dict) or "id" not in doc:
            continue
        up = doc.get("upstream") or {}
        for n in (str(doc["id"]).rsplit("/", 1)[-1], (doc.get("component") or {}).get("ships_as"),
                  up.get("name")):
            if norm_name(n):
                names.setdefault(norm_name(n), doc["id"])
    return names


def records(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        for name in z.namelist():
            if name.endswith(".json"):
                try:
                    yield json.loads(z.read(name))
                except ValueError:
                    continue


def analyse_git(zip_path):
    repos = defaultdict(lambda: {"urls": set(), "cves": set(), "records": 0, "c_sigs": 0,
                                 "sig_files": set(), "years": [], "ids": set()})
    for rec in records(zip_path):
        cves = set(CVE_RE.findall(" ".join([rec.get("id", ""), *rec.get("aliases", [])])))
        year = (rec.get("published") or "")[:4]
        for aff in rec.get("affected", []):
            sigs = (aff.get("database_specific") or {}).get("vanir_signatures") or []
            c_files = [s["target"]["file"] for s in sigs
                       if str((s.get("target") or {}).get("file", "")).lower().endswith(C_EXT)]
            for rng in aff.get("ranges", []):
                if rng.get("type") != "GIT":
                    continue
                key = repo_key(rng.get("repo"))
                if not key:
                    continue
                r = repos[key]
                r["urls"].add(rng["repo"])
                r["cves"] |= cves
                r["ids"].add(rec["id"])
                r["records"] += 1
                r["c_sigs"] += len(c_files)
                r["sig_files"].update(c_files[:5])
                if year.isdigit():
                    r["years"].append(int(year))
    return repos


FAMILIES = {  # label -> (OSV ecosystem prefix, purl prefix)
    "debian": ("Debian", "pkg:deb/debian/"),
    "ubuntu": ("Ubuntu", "pkg:deb/ubuntu/"),
    "alpine": ("Alpine", "pkg:apk/alpine/"),
}


def distro_aliases(zip_path, cve_to_repos, ecosystem):
    """repo key -> {source package: shared CVE count} for one distribution's dump."""
    out = defaultdict(lambda: defaultdict(set))
    for rec in records(zip_path):
        cves = set(CVE_RE.findall(" ".join([rec.get("id", ""), *rec.get("aliases", []),
                                            *rec.get("upstream", [])])))
        pkgs = {a["package"]["name"] for a in rec.get("affected", [])
                if (a.get("package") or {}).get("ecosystem", "").startswith(ecosystem)}
        for cve in cves:
            for repo in cve_to_repos.get(cve, ()):
                for p in pkgs:
                    out[repo][p].add(cve)
    return {repo: {p: len(c) for p, c in pk.items()} for repo, pk in out.items()}


def debian_aliases(zip_path, cve_to_repos):
    return distro_aliases(zip_path, cve_to_repos, "Debian")


def alias_candidates(rows, deb_like, rule_meta, rule_keys):
    """For each covered upstream: the distro purls to add as ``upstream.identifiers``.

    A package qualifies when it carries at least half as many of the upstream's CVEs as the
    best package of its distribution (dependents carry few), and is marked ``name`` when
    its name matches a name the rule goes by, ``review`` otherwise.
    """
    by_id = {rid: m for rid, m in rule_meta.items()}
    result = []
    for x in rows:
        rid = x["covered_by"]
        if not rid or rid not in by_id:
            continue
        meta = by_id[rid]
        have = {i.lower().split("?")[0] for i in meta["identifiers"]}
        proposals = []
        for fam, (_, prefix) in FAMILIES.items():
            counts = deb_like.get(fam, {}).get(x["purl"], {})
            if not counts:
                continue
            top = max(counts.values())
            for pkg, n in sorted(counts.items(), key=lambda kv: -kv[1]):
                if n * 2 < top or n < 2:
                    continue
                purl = f"{prefix}{pkg}"
                if purl.lower() in have:
                    continue
                same_name = norm_name(pkg) in meta["names"] or any(
                    norm_name(pkg).startswith(nm) or nm.startswith(norm_name(pkg))
                    for nm in meta["names"] if len(nm) >= 3)
                # A matching name is not enough on its own: Ubuntu's `zephyr` is MIT's
                # notification system and shares 19 of the RTOS's 274 CVEs by coincidence of
                # name. It must also carry a real share of the upstream's CVEs.
                confidence = "name" if same_name and n * 10 >= x["cves"] * 3 else "review"
                proposals.append({"purl": purl, "shared_cves": n, "of": x["cves"],
                                  "confidence": confidence})
        if proposals:
            result.append({"rule": rid, "file": meta["path"], "upstream": meta["purl"],
                           "existing": meta["identifiers"], "add": proposals})
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--git", required=True, help="OSV GIT/all.zip")
    ap.add_argument("--debian", help="OSV Debian/all.zip (adds distro aliases)")
    ap.add_argument("--ubuntu", help="OSV Ubuntu/all.zip")
    ap.add_argument("--alpine", help="OSV Alpine/all.zip")
    ap.add_argument("--alias-candidates", metavar="OUT.json",
                    help="write upstream.identifiers candidates for covered rules (needs a distro dump)")
    ap.add_argument("--alias-md", metavar="OUT.md", help="the same as a table for review")
    ap.add_argument("--rules", default=str(Path(__file__).resolve().parent.parent / "rules"))
    ap.add_argument("--top", type=int, default=300)
    ap.add_argument("--min-cves", type=int, default=3)
    ap.add_argument("--hints", default=str(Path(__file__).resolve().parent / "embedded_hints.txt"),
                    help="file of embedded-relevant repo names (ranking aid)")
    ap.add_argument("--embedded-only", action="store_true", help="keep only hinted repos")
    ap.add_argument("--include-covered", action="store_true")
    ap.add_argument("--out-md")
    ap.add_argument("--out-json")
    a = ap.parse_args()

    hints = set()
    if a.hints and Path(a.hints).exists():
        hints = {norm_name(l) for l in Path(a.hints).read_text().splitlines()
                 if l.strip() and not l.startswith("#")}
    rule_keys = load_rule_keys(a.rules)
    rule_names = load_rule_names(a.rules)
    repos = analyse_git(a.git)
    cve_to_repos = defaultdict(set)
    for key, r in repos.items():
        for c in r["cves"]:
            cve_to_repos[c].add(key)
    deb = debian_aliases(a.debian, cve_to_repos) if a.debian else {}
    dumps = {"debian": a.debian, "ubuntu": a.ubuntu, "alpine": a.alpine}
    by_family = {}
    for fam, path in dumps.items():
        if path and (a.alias_candidates or a.alias_md):
            by_family[fam] = deb if fam == "debian" else distro_aliases(path, cve_to_repos, FAMILIES[fam][0])
    if "debian" not in by_family and a.debian:
        by_family["debian"] = deb

    rows = []
    for key, r in repos.items():
        if r["c_sigs"] == 0 or len(r["cves"]) < a.min_cves:
            continue
        rule = rule_keys.get(key)
        base = key.rsplit("/", 1)[-1]
        by_name = rule_names.get(norm_name(base))
        pk = sorted(deb.get(key, {}).items(), key=lambda kv: -kv[1])
        # CVEs of a library also land on its dependents (curl -> wget); keep only
        # packages carrying at least half as many of the CVEs as the best one.
        pk = [kv for kv in pk if pk and kv[1] * 2 >= pk[0][1]]
        rows.append({
            "purl": key, "url": sorted(r["urls"])[0], "cves": len(r["cves"]),
            "c_signatures": r["c_sigs"], "sample_files": sorted(r["sig_files"])[:3],
            "last_cve_year": max(r["years"]) if r["years"] else None,
            "debian_packages": [p for p, _ in pk[:3]],
            "embedded_hint": norm_name(base) in hints or any(
                norm_name(p) in hints for p in deb.get(key, {})),
            "covered_by": rule, "name_match": None if rule else by_name,
            "_cves": r["cves"]})
    rows.sort(key=lambda x: (-x["cves"], x["purl"]))
    # one project, several hosts (github + gitlab + project git): fold repos whose
    # CVE sets overlap by 80%+ into the biggest one and list the others as mirrors.
    kept = []
    for x in rows:
        for k in kept:
            inter = len(x["_cves"] & k["_cves"])
            if inter and inter / min(len(x["_cves"]), len(k["_cves"])) >= 0.8:
                k.setdefault("mirrors", []).append(x["purl"])
                k["covered_by"] = k["covered_by"] or x["covered_by"]
                k["name_match"] = k["name_match"] or x["name_match"]
                k["embedded_hint"] = k["embedded_hint"] or x["embedded_hint"]
                k["debian_packages"] = k["debian_packages"] or x["debian_packages"]
                break
        else:
            kept.append(x)
    rows = kept
    for x in rows:
        del x["_cves"]
    missing = [x for x in rows if not x["covered_by"]]
    likely = [x for x in missing if x["name_match"]]
    shown = rows if a.include_covered else missing
    if a.embedded_only:
        shown = [x for x in shown if x["embedded_hint"]]
    shown = shown[:a.top]

    if a.alias_candidates or a.alias_md:
        cands = alias_candidates(rows, by_family, load_rule_meta(a.rules), rule_keys)
        if a.alias_candidates:
            Path(a.alias_candidates).write_text(json.dumps(cands, indent=1, ensure_ascii=False))
        if a.alias_md:
            out = ["# upstream.identifiers candidates\n",
                   "Generated by `tools/gap_analysis.py --alias-candidates`. `name`: the package name matches a "
                   "name the rule goes by and it carries 30%+ of the upstream's CVEs; `review`: it shares CVEs but its name does not match (often a "
                   "dependent or a bundled copy), so check it before adding.\n",
                   "| rule | add | shared CVEs | confidence |", "|---|---|---|---|"]
            for c in cands:
                for p in c["add"]:
                    out.append(f"| `{c['rule']}` | `{p['purl']}` | {p['shared_cves']}/{p['of']} | {p['confidence']} |")
            Path(a.alias_md).write_text("\n".join(out) + "\n")
        print(f"{len(cands)} rules with candidates, "
              f"{sum(len(c['add']) for c in cands)} identifiers", file=sys.stderr)

    summary = {"c_cpp_repos_with_cves": len(rows), "covered": len(rows) - len(missing),
               "missing": len(missing), "missing_but_name_matches_a_rule": len(likely), "rules_indexed": len(set(rule_keys.values()))}
    if a.out_json:
        Path(a.out_json).write_text(json.dumps({"summary": summary, "rows": shown}, indent=1, ensure_ascii=False))
    lines = ["# Rule gap analysis (OSV GIT, C/C++ upstreams)\n",
             f"C/C++ repos with >= {a.min_cves} CVEs: **{summary['c_cpp_repos_with_cves']}**; "
             f"covered by a rule: **{summary['covered']}**; missing: **{summary['missing']}** "
             f"(rules indexed: {summary['rules_indexed']}).\n",
             "| # | upstream (mirrors) | CVEs | last | debian | emb | covered / name match |", "|---|---|---|---|---|---|---|"]
    for i, x in enumerate(shown, 1):
        mir = f" (+{len(x['mirrors'])})" if x.get("mirrors") else ""
        cov = x["covered_by"] or (f"name: {x['name_match']}" if x["name_match"] else "")
        lines.append(f"| {i} | `{x['purl']}`{mir} | {x['cves']} | {x['last_cve_year']} | "
                     f"{', '.join(x['debian_packages'])} | {'★' if x['embedded_hint'] else ''} | {cov} |")
    md = "\n".join(lines) + "\n"
    if a.out_md:
        Path(a.out_md).write_text(md)
    else:
        print(md)
    print(json.dumps(summary), file=sys.stderr)


if __name__ == "__main__":
    main()
