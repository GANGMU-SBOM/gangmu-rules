# 纲目规则库 · gangmu-rules

**免费的规则库：被各家 SDK 拷贝最多的上游开源组件，社区共同维护。**

[![rules](https://github.com/GANGMU-SBOM/gangmu-rules/actions/workflows/rules.yml/badge.svg?branch=main)](https://github.com/GANGMU-SBOM/gangmu-rules/actions/workflows/rules.yml)
[![PyPI](https://img.shields.io/pypi/v/gangmu-rules.svg)](https://pypi.org/project/gangmu-rules/)

[纲目 Gangmu](https://github.com/GANGMU-SBOM/gangmu) 用这份规则库在嵌入式 C/C++ 源码树里认出被改名、魔改、
静态链接的开源组件，并生成 SBOM。工具和规则分开维护：工具按版本发布，规则按日期发布，
新增一条规则不用等工具发版。

[English](README.en.md) · [贡献规则](CONTRIBUTING.md) · [规则格式](https://github.com/GANGMU-SBOM/gangmu/blob/main/docs/RULE-FORMAT.md)

## 安装

```bash
pip install gangmu-sbom      # 会一并装上 gangmu-rules
pip install -U gangmu-rules  # 只更新规则
gangmu rules lint            # 查看当前加载了哪些规则
```

无法访问 PyPI 的内网环境：从 [Releases](https://github.com/GANGMU-SBOM/gangmu-rules/releases) 下载
`gangmu-rules-offline-<版本>.tar.gz`，解压后用 `SHA256SUMS` 校验，再设置 `GANGMU_RULES=<解压目录>`。

## 里面有什么

| 目录 | 内容 |
| --- | --- |
| `rules/generic/` | 被各家 SDK 拷贝最多的上游组件：lwIP、Mbed TLS、FreeRTOS、RT-Thread、LiteOS、GmSSL、铜锁、wolfSSL 等 |
| `rules/zephyrproject/` | Zephyr 及其 HAL 模块 |

共 60 条规则，全部免费，欢迎社区贡献。

## 厂商专属的规则

只跟一家公司绑定的规则（这家公司自己的 SDK、固件库，或它 fork 过的开源组件）不在这个免费规则库里，属于商业版规则包。
规则 id 与这里一致，装上商业版规则包后自动叠加；只装这个仓库时，这些公司的固件库不会被认出来。

每条规则都写明它对应的上游版本（固定的标签或提交），CI 会从这个上游重新推导证据，复现不了的规则不会合入。

## 叠加自己的规则

自有 BSP、未公开的 SDK，可以写在自己的目录里，扫描时叠加在社区规则之上；同一个 id 以后加载的为准：

```bash
gangmu scan firmware/ --rules "$(python -c 'import gangmu_rules;print(gangmu_rules.path())')" --rules my-rules/
```

也可以把私有规则做成 Python 包，通过 `gangmu.rule_packs` 入口自动加载（见本仓库的 `pyproject.toml`）。

## 相关仓库

| 仓库 | 做什么 |
| --- | --- |
| [gangmu](https://github.com/GANGMU-SBOM/gangmu) | 工具本体：扫描、SBOM、漏洞比对、CRA 与工信部草稿。工具本身的问题去那里提 |
| **gangmu-rules**（本仓库） | 免费规则库：认不出某个 SDK 里的通用组件、认错了版本，在这里提 issue 或 PR |
| [gangmu-bench](https://github.com/GANGMU-SBOM/gangmu-bench) | 评测：用真实上游发布版检验规则认得对不对，每次规则变动后都可以重跑 |

商业版在开源版之上叠加持续监测、报送工作台和规则企业服务，见[开源版与商业版](https://github.com/GANGMU-SBOM/gangmu/blob/main/docs/EDITIONS.md)。

## 参与规则共建，联系我们

一条规则只需要一个干净的上游版本和一次 `gangmu rules verify`，欢迎大家一起补。

- **通用开源组件、Zephyr 与 HAL、国产 SDK 里常见的第三方库**：直接提 issue 或 PR，见 [CONTRIBUTING.md](CONTRIBUTING.md)；
- **想认领某个芯片 SDK、不确定规则该放哪里、手上有真实固件样本愿意帮忙验证**：先联系我，避免重复劳动；
- **厂商专属规则、私有 BSP、商业版规则包**：同样联系我。

联系方式：邮箱 64031875@qq.com，或扫码进「CRA 合规群」（二维码有有效期，扫不出来请发邮件）。

<img src="docs/assets/cra-wechat-group.png" alt="CRA 合规群二维码" width="200">

你贡献的规则按本仓库的许可证（CDLA-Permissive-2.0）授权；已有内容不会撤回，也不会收费。


## 许可证

规则数据采用 [CDLA-Permissive-2.0](rules/LICENSE)，任何项目和产品都可以使用；打包代码采用 Apache-2.0。

厂商专属规则包、带响应时限的规则更新、离线镜像或为自有 SDK 编写私有规则，见[开源版与商业版](https://github.com/GANGMU-SBOM/gangmu/blob/main/docs/EDITIONS.md)。
