# frida-modified

一个支持 Codex、Claude Code、Cursor、Gemini CLI、GitHub Copilot 和 OpenCode 的 Agent Skill，按目标 Android 设备选版：识别环境、推荐候选版本、获取官方源码与产物、建立原版基线、适配修改、构建、对照验证和部署。

附带 Frida `17.18.0` 的 commit 固定补丁与 Linux x86_64 构建适配。版本选择不会默认套用最新版本；其他版本按实际源码和目标设备补充适配。当前案例来自 Pixel 3 / Android 12，Android 10 尚无本项目的实机验证。

## 一键安装

先安装 Node.js **22.20.0+**（含 npm/npx）和 Git。在终端执行以下一条命令，同时安装到 Codex 和 Claude Code，所有项目均可使用：

```bash
npx --yes skills@1.5.26 add johnsonconnor97815/frida-modified --skill frida-modified --agent codex claude-code --global --yes
```

只安装到一个 Agent 时，将 `--agent codex claude-code` 改为 `--agent codex` 或 `--agent claude-code`。也可以一次安装到以下 6 个常用 Agent：

```bash
npx --yes skills@1.5.26 add johnsonconnor97815/frida-modified --skill frida-modified --agent codex claude-code cursor gemini-cli github-copilot opencode --global --yes
```

去掉 `--global` 即安装到当前项目；Windows 可以追加 `--copy` 使用文件复制。命令固定使用已验证的 `skills` CLI `1.5.26`，Skill 内容取自本仓库的默认分支。`--yes` 会直接替换安装目录中的同名 Skill；旧版手动软链迁移、固定版本安装、更新和卸载见 [安装说明](INSTALL.md)。

## 使用

Codex 中输入：

```text
使用 $frida-modified，先识别我指定的 Android 设备，根据环境推荐 Frida 版本，再规划需要修改的标识，完成构建和对照测试。
```

Claude Code 中输入：

```text
/frida-modified 先识别我指定的 Android 设备，根据环境推荐 Frida 版本，再规划需要修改的标识，完成构建和对照测试。
```

其他 Agent 可要求“使用 frida-modified Skill”，或通过其技能菜单选择。安装后若未出现，重启对应 Agent 会话。

脚本要求 Python 3.10+、Git；设备操作需要 ADB，功能测试需要与目标产物匹配的 Python `frida`。构建、SDK/NDK 和 Java bridge 的条件按所选版本确定。当前构建适配器针对 Linux x86_64。安装到 Windows/macOS 不代表这些平台已支持 Frida 构建；设备脚本使用 POSIX `fcntl`，Windows 上应在 WSL/Linux 中执行。

- [Skill 入口](skills/frida-modified/SKILL.md)
- [操作步骤](skills/frida-modified/references/workflow.md)
- [版本选择](skills/frida-modified/references/version-selection.md)
- [17.18.0 补丁与构建](skills/frida-modified/references/case-17.18.0.md)
- [部署与恢复边界](skills/frida-modified/references/deployment.md)
- [固定 App 回归](skills/frida-modified/references/app-regression.md)

## 验证

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q skills/frida-modified/scripts
```

行为测试使用隔离文件和受控设备替身，检查版本/补丁约束、输入指纹、资源所有权、部署恢复及清理失败。实机、构建和 App 验证结果另见 [VALIDATION.md](VALIDATION.md)。单元测试通过不代表某个 Android 版本兼容。安装 CI 另在 Linux、macOS、Windows 检查 6 个 Agent 的项目级/全局安装、重复安装、资源完整性和卸载；复现方法见 [安装说明](INSTALL.md#安装验证)。

本仓库分发 Skill、脚本、源码补丁及测试资源；使用者的 APK、设备序列号、本机路径、原始日志与运行产物保存在各自工作目录。功能正常、名称修改生效和目标 App 的检测结果分别记录。

原创 Skill、脚本和测试采用 [MIT License](LICENSE)。Frida 源码补丁沿用其上游许可，见 [NOTICE.md](NOTICE.md)。
