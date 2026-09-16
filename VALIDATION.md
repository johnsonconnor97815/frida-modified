# v0.1.0 验证记录

验证日期：2026-09-16 UTC。环境为 Linux x86_64、Pixel 3 / Android 12 / API 31 / ARM64，Frida `17.18.0`，frida-tools `14.10.4`。构建使用 NDK `29.0.14206865`、JDK 17、Android SDK API 29 和 build-tools `36.0.0`。

| 检查 | 结果与范围 |
| --- | --- |
| Skill 格式 | `quick_validate.py` 通过 |
| 行为测试 | 23 项通过；覆盖未知环境、多设备歧义、版本/补丁约束、缓存输入及产物失配、PID 复用、退出竞态、部署恢复和清理失败 |
| 补丁重放 | 在独立干净源码树上检查、应用两个修改组；绑定上游及子模块 commit |
| 资源同步 | helper DEX 重建；四种嵌入 Zymbiote ELF 的已知输入和修改后哈希校验通过 |
| Android 构建 | 完整构建 server、ARM64/ARM32 Agent/Gadget；核对产物哈希及 Agent/Gadget SONAME |
| 主机客户端 | 完整构建 Python wheel，安装到独立 venv 后参与重建版实机测试 |
| 官方原版对照 | 从官方 release 下载 ARM64 server；两轮 App 测试，共 102 项检查、10 张截图，清理通过 |
| 重建版 native | ARM64 QJS attach、V8 native spawn，Hook、RPC、文件读取、卸载/detach 及清理通过 |
| 重建版 Gadget | ARM64 与 ARM32 harness 的加载、Hook/RPC、文件读取和完整 `dlclose` 通过 |
| 重建版 App | 相同 APK、输入和场景下两轮测试，共 102 项检查、10 张截图，清理通过 |
| 真实部署失败恢复 | 以无效启动参数让候选 server 退出；部署判为失败，旧产物、参数、身份恢复并通过注入复测 |
| 最终设备状态 | 恢复验证前的原魔改 server 产物及启动参数，核对运行哈希并通过注入复测 |

官方版与重建版使用固定 OWASP UnCrackable Level 1 APK。在相同输入下检查 `Nope... → Success! → 卸载后 Nope...`，并覆盖 QJS App spawn、V8 reattach、Java/native Hook、RPC 和二进制消息。两组共 204 项检查通过。

首次迁移测试曾出现一次启动期 ART `SIGSEGV`。随后将非启动期 native 检查移到界面就绪后，再完成上述原版与重建版对照。失败记录被保留；这不足以证明该崩溃的根因已彻底消除，也不代表所有启动时序均稳定。

本轮 native attach/spawn 和 Java 场景使用 ARM64；ARM32 使用 Gadget harness。Android 10、ARM32 Java、APK 内 Gadget 集成及任意 App 的反 Frida 检测效果仍未验证。SELinux 策略没有被声称完整回滚。

[机器可读摘要](validation/summary.json) 包含验证范围与实际产物哈希。验证源树由现有官方 Git 对象创建独立干净 checkout；官方 server 则通过本 Skill 的下载脚本重新取得。原始设备日志、截图、失败记录及完整构建记录保存在实施者工作目录，不随仓库发布。
