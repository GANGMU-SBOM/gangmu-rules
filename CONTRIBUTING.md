# 贡献规则 · Contributing a rule

规则是这个项目价值最集中的地方，而且一条规则的成本很低。Rules are where almost all
the value is, and a rule is cheap to add.

You need the tool: `pip install gangmu-sbom` (or `pip install -e .` in a checkout of
[gangmu](https://github.com/GANGMU-SBOM/gangmu)), then `pip install -e .` here so
`gangmu` picks this checkout up as the community rule pack.

## Does the rule go here?

This repository is the free rule base: the general upstream components many vendor SDKs copy (lwIP, Mbed TLS,
FreeRTOS, LVGL, open-source kernels), Zephyr and its HAL modules, and rules contributed by the community. A rule tied
to a single company, that is its own SDK, its firmware library, or an open-source component only that company
forked, is part of the commercial rule packs and is not accepted here. If in doubt, open an issue or email
64031875@qq.com first; whoever reviews it will say whether it goes here. **If you want to take on a chip SDK, tell
us before you start**, so that work is not duplicated and we can point you at the cheapest route.

## Adding a rule

Rules are where almost all the value is, and a rule is cheap to add.

1. Get the pristine upstream release.

   ```bash
   git clone --depth 1 --branch STABLE-2_2_0_RELEASE https://github.com/lwip-tcpip/lwip
   ```

2. Generate the identity block.

   ```bash
   gangmu rules fingerprint lwip --version 2.2.0 \
       --include 'src/**/*.c' --include 'src/**/*.h' \
       --anchor src/core/init.c
   ```

3. Write `rules/generic/<component>.yaml` (or `rules/<project>/<sdk>/<component>.yaml` for a project like Zephyr) using
   [RULE-FORMAT.md](https://github.com/GANGMU-SBOM/gangmu/blob/main/docs/RULE-FORMAT.md). Find the real CPE on
   [NVD](https://nvd.nist.gov/products/cpe/search) -- do not invent one. A CPE
   with the wrong vendor silently matches nothing.

4. Check it reproduces, then open the pull request.

   ```bash
   gangmu rules lint
   gangmu rules verify --rules rules --rule generic/lwip
   ```

CI does step 4 again from scratch, runs gangmu's own test suite and its
performance check against your branch, fetching exactly the release your rule names.
Review is therefore mostly about metadata: is the CPE right, is the licence
right, is the fork note honest.

### What makes a good rule

* **Anchor on files that do not move.** A version header or a core source file,
  not a config file the vendor is certain to edit.
* **Scope `include` to upstream's own code.** If the vendor's directory also
  holds a port layer they wrote, excluding it keeps similarity meaningful.
* **Say when it is a fork.** `vendor_fork.patched: true` plus a one-line note is
  worth more to an auditor than a higher confidence score.
* **Do not raise `confidence_ceiling` above 0.95.** Nothing here is certain.
* **Record why there is no CPE.** `cpe_status` distinguishes "none exists in
  NVD" from "nobody looked", and those are very different facts to an auditor.
  `gangmu rules lint` fails on a rule that has neither a CPE nor a reason.

### What we will not merge

* A rule with no `upstream.source`, or one pointing at a moving ref such as a
  branch name. Pin a tag or a commit.
* A rule whose evidence does not reproduce in CI.
* A CPE that does not exist in NVD.
* A signature generated from a vendor tree while the rule claims upstream.
  (The first version of the shipped cJSON rule did exactly this and CI caught
  it -- the signature came from `HEAD`, the rule said `v1.7.19`.)

## Sign your commits (DCO)

We use the [Developer Certificate of Origin](https://developercertificate.org/)
instead of a CLA. Add `Signed-off-by` with `git commit -s`; it certifies that you
have the right to contribute the change under this repository's licences
(CDLA-Permissive-2.0 for rule data, Apache-2.0 for code). The commercial edition is built on top of this open-source
base and may include contributed rules under those licences; what is published here is never withdrawn or put behind
a fee. If you work for a
silicon vendor or an ODM, make sure you are allowed to publish the fingerprints
of the SDK you are describing. Fingerprints and metadata only: never commit
vendor source code.

## Maintainers

`.github/CODEOWNERS` assigns each `rules/<directory>/` to its reviewers. A project
that wants to look after its own rules can ask to be added there.

## Releasing

1. Bump the date version in three places: `pyproject.toml`,
   `src/gangmu_rules/__init__.py` and `rules/rulebase.json` (CI checks they agree).
   Raise `requires_gangmu` in `rules/rulebase.json` if a rule uses a field only a
   newer gangmu understands.
2. Tag `vYYYY.MM.N` on main. The release workflow publishes the wheel to PyPI and
   an offline tarball with `SHA256SUMS` to GitHub Releases.
