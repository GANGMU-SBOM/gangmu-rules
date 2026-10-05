# 安全政策 · Security Policy

[English below](#english)

## 规则错误也按安全问题对待

规则库里写错的 CPE、错标的版本或漏认的厂商 fork，会让 SBOM 看起来是干净的，实际却漏掉了漏洞。
这类问题请用「组件识别请求」issue 模板公开报告，并附上能复现的上游版本；它们会被优先处理。

## 报告安全漏洞

如果你发现的是本仓库发布流程或打包代码的安全问题，请**不要**公开提 issue，而是通过本仓库的
[私密漏洞报告](https://github.com/GANGMU-SBOM/gangmu-rules/security/advisories/new)提交。
我们会在 5 个工作日内确认收到，并与你协调修复和公开的时间。扫描工具本身的漏洞请报到
[gangmu](https://github.com/GANGMU-SBOM/gangmu/security/advisories/new)。

## 支持的版本

只有最新发布的规则库（按日期编号）会收到修复。

---

## English

**Rule errors are treated as security issues.** A wrong CPE, a mislabelled version or a missed vendor fork makes an
SBOM look clean while hiding vulnerabilities. Report these publicly with the component identification issue template
and a reproducible upstream release; they are prioritised.

**Vulnerabilities in the release process or packaging code** of this repository: please do not open a public issue.
Use this repository's
[private vulnerability reporting](https://github.com/GANGMU-SBOM/gangmu-rules/security/advisories/new). We acknowledge
within five working days and coordinate a fix and disclosure date with you. Vulnerabilities in the scanner itself go to
[gangmu](https://github.com/GANGMU-SBOM/gangmu/security/advisories/new).

**Supported versions:** only the latest dated release of the rule base receives fixes.
