# gangmu-rules

**The free rule base: the upstream open-source components that vendor SDKs copy most, maintained by the community.**

[![rules](https://github.com/GANGMU-SBOM/gangmu-rules/actions/workflows/rules.yml/badge.svg?branch=main)](https://github.com/GANGMU-SBOM/gangmu-rules/actions/workflows/rules.yml)
[![PyPI](https://img.shields.io/pypi/v/gangmu-rules.svg)](https://pypi.org/project/gangmu-rules/)

[Gangmu (纲目)](https://github.com/GANGMU-SBOM/gangmu) uses this rule base to recognise renamed, modified and
statically linked open-source components in embedded C/C++ trees and to produce an SBOM. The tool and the rules
are released separately: the tool by version, the rules by date, so a new rule never waits for a tool release.

[中文](README.md) · [Contributing a rule](CONTRIBUTING.md) · [Rule format](https://github.com/GANGMU-SBOM/gangmu/blob/main/docs/RULE-FORMAT.md)

## Install

```bash
pip install gangmu-sbom      # pulls in gangmu-rules
pip install -U gangmu-rules  # update the rules only
gangmu rules lint            # show which rules are loaded
```

Air-gapped: download `gangmu-rules-offline-<version>.tar.gz` from Releases, check it against `SHA256SUMS`, and set
`GANGMU_RULES` to the unpacked directory.

## What is in it

89 rules, all free: `rules/generic/` (lwIP, Mbed TLS, FreeRTOS, RT-Thread, LiteOS, GmSSL, Tongsuo, wolfSSL and the other
upstream components SDKs copy most) and `rules/zephyrproject/` (Zephyr and its HAL modules). Contributions welcome.

`rules/patches/` holds **patch records**: for an advisory, the functions its fix changed, so `gangmu vuln --source ROOT` can
tell whether the *fix* is in a vendor's copy instead of guessing from the version (9 records so far: nanopb, nimble, wolfSSL,
libjpeg-turbo). Every record is rebuilt from its upstream commits in CI. See
[CONTRIBUTING.md](CONTRIBUTING.md#adding-a-patch-record).

## Vendor-specific rules

Rules tied to one company (its SDK, its firmware library, or an open-source component it forked) are not in this free rule base; they are commercial rule packs.
Rule ids are the same as here, so installing a commercial pack loads them automatically; with only this repository those companies' firmware libraries are not recognised.

## Your own rules on top

Pass `--rules` more than once; a later directory's rule replaces an earlier one with the same id. A private rule
set can also be shipped as a Python package that registers a `gangmu.rule_packs` entry point, as this one does.

## Related repositories

| Repository | What it is |
| --- | --- |
| [gangmu](https://github.com/GANGMU-SBOM/gangmu) | The tool: scanning, SBOMs, vulnerability matching, CRA and MIIT drafts. Tool bugs go there |
| **gangmu-rules** (this repo) | The free rule base: a general component in some SDK is not recognised, or the version is wrong; open an issue or PR here |
| [gangmu-bench](https://github.com/GANGMU-SBOM/gangmu-bench) | The benchmark: checks the rules against real upstream releases; rerun it after any rule change |

The commercial edition adds continuous monitoring, a reporting workbench and rule services on top of the open-source
one; see [editions](https://github.com/GANGMU-SBOM/gangmu/blob/main/docs/EDITIONS.md#open-source-and-commercial-editions).

## Contribute rules, get in touch

A rule takes one clean upstream release and one run of `gangmu rules verify`; help is welcome.

- **General open-source components, Zephyr and its HALs, third-party libraries found in Chinese SDKs:** open an issue or pull request; see [CONTRIBUTING.md](CONTRIBUTING.md).
- **Want to take on a chip SDK, unsure where a rule belongs, or have real firmware samples to help verify:** contact me first so we do not duplicate work.
- **Vendor-specific rules, private BSPs, commercial rule packs:** contact me as well.

Contact: email 64031875@qq.com, or join the WeChat "CRA compliance group" (the QR code expires; email if it does not scan).

<img src="docs/assets/cra-wechat-group.png" alt="WeChat group QR code" width="200">

Rules you contribute are licensed under this repository's licence (CDLA-Permissive-2.0). Existing content will not be withdrawn or put behind a fee.

## Licence

Rule data: [CDLA-Permissive-2.0](rules/LICENSE), usable by any project or product. Packaging code: Apache-2.0.

Vendor-specific rule packs, rule updates with a response-time commitment, offline mirrors and private rules for your own SDKs are part of the
[commercial edition](https://github.com/GANGMU-SBOM/gangmu/blob/main/docs/EDITIONS.md#open-source-and-commercial-editions).

