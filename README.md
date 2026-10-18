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
| `rules/generic/` | 被各家 SDK 拷贝最多的上游组件：lwIP、Mbed TLS、Mbed Crypto、eRPC、PCRE2、libssh2、Brotli、yyjson、libevent、json-c、LibTomMath、nng、libmosquitto、libogg、libvorbis、FLAC、libwebp、LibTIFF、libusb、libdeflate、wasm3、libcbor、mruby、zlib-ng、libzip、xxHash、libuv、bzip2、http-parser、libconfig、cyw43-driver、libffi、WIZnet ioLibrary、inih、flatcc、libIEC61850、lib60870、Azure C 共享库、uMQTT、uAMQP、Azure SDK for C、ChibiOS/RT、RIOT 内核、Mbed OS 核心层与网络层、RIOT 系统库与设备驱动、FreeRTOS、RT-Thread、LiteOS、GmSSL、铜锁、wolfSSL，以及 zlib、libpng、curl、Expat、LZ4、Lua、ThreadX、NetX Duo、FileX、USBX、GUIX、LevelX、CMSIS-Core、CMSIS-DSP、CMSIS-NN、CMSIS-RTX、mJS、Elk、msgpack-c、SPIFFS、libcsp、MPack、Unity、libcanard、lwext4、CMSIS-Driver、coreMQTT Agent、FreeRTOS Cellular Interface、µC/OS-II、µC/OS-III 及 µC/LIB、CPU、FS、TCP-IP、Common、BTstack、zstd、LibTomCrypt、U8g2、Contiki-NG、Mynewt、NuttX、wolfMQTT、wolfBoot、wolfSSH、wolfTPM、Paho 嵌入式 C、heatshrink、coreHTTP、coreJSON、corePKCS11、AWS IoT 嵌入式 SDK 各库、WAMR、coreMQTT、TinyUSB、MCUboot、FreeRTOS-Plus-TCP、libsodium、Mongoose、MicroPython、Jansson、libxml2、c-ares、Newlib 等 |
| `rules/zephyrproject/` | Zephyr 及其 HAL 与库模块（Zephyr 4.4 的 west 清单里除测试和仿真外的全部模块，含 ADI、Ambiq、Atmel、Espressif、Microchip、Nuvoton、树莓派 Pico、ST 等厂商 HAL，以及 picolibc、CMSIS 6、LC3、MCTP、SEGGER RTT 等） |
| `rules/patches/` | 补丁记录：某条公告的修复改了哪些函数。`gangmu vuln --source ROOT` 据此判断厂商那份代码里**修复本身**在不在，而不是只看版本号去猜（目前 9 条：nanopb、nimble、wolfSSL、libjpeg-turbo）。每条记录在 CI 里都从它写明的上游提交重新生成并比对，见 [CONTRIBUTING.md](CONTRIBUTING.md#adding-a-patch-record) |

共 223 条规则，全部免费，欢迎社区贡献。

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
| [gangmu-cbom-rules](https://github.com/GANGMU-SBOM/gangmu-cbom-rules) | 密码算法与库能力表：`gangmu cbom` 读的规则，格式和本仓库不同 |
| [gangmu-action](https://github.com/GANGMU-SBOM/gangmu-action) | GitHub Action：在 CI 里生成 SBOM、CBOM 并给出后量子就绪报告 |

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
