# 安装 frida-modified

本仓库同时提供 Codex 原生插件、Claude Code 原生插件和标准 `SKILL.md`。插件和普通 Skill 使用同一份 `skills/frida-modified/` 内容。选择一种方式即可，避免同名技能重复出现。

## Codex CLI 原生 Git 安装

在终端执行：

```bash
codex plugin marketplace add johnsonconnor97815/frida-modified
codex plugin add frida-modified@frida-modified
```

第一条命令克隆仓库并注册其中的插件市场；第二条安装市场中的插件。完整 Git URL `https://github.com/johnsonconnor97815/frida-modified.git` 也可以作为第一条命令的参数。

打开新的 Codex 会话，通过 `/plugins` 查看插件，输入 `$` 选择它提供的 `frida-modified` Skill。需要固定版本时，首次添加市场可追加 `--ref v0.1.2`。

更新默认分支上的插件：

```bash
codex plugin marketplace upgrade frida-modified
codex plugin add frida-modified@frida-modified
```

卸载：

```bash
codex plugin remove frida-modified@frida-modified
codex plugin marketplace remove frida-modified
```

命令依据 [Codex CLI 官方文档](https://developers.openai.com/codex/cli/reference#codex-plugin)。本项目用 `codex-cli 0.154.0` 验证；插件命令在官方文档中仍标为实验功能。先用 `codex plugin --help` 检查当前版本；没有该子命令时，可以使用下面的内置 Skill 安装器。

### 在 Codex 会话里直接给出仓库

输入下面这句话即可：

```text
使用 $skill-installer 从 https://github.com/johnsonconnor97815/frida-modified 安装 skills/frida-modified。
```

这是普通 Skill 安装方式，使用 Codex 内置的 `$skill-installer`，无需插件市场或 Node.js。安装后下一轮可用 `$frida-modified`；若未出现，重启会话。已存在同名目录时，安装器会停止，先处理已有版本再安装。

## Claude Code CLI 原生 Git 安装

在 Claude Code 交互会话里依次输入：

```text
/plugin marketplace add johnsonconnor97815/frida-modified
/plugin install frida-modified@frida-modified
/reload-plugins
```

也可以直接从终端安装到用户范围：

```bash
claude plugin marketplace add johnsonconnor97815/frida-modified
claude plugin install frida-modified@frida-modified --scope user
```

市场参数也接受完整 Git URL。插件版使用命名空间调用：

```text
/frida-modified:frida-modified 先识别指定的 Android 设备，再推荐 Frida 版本并规划修改。
```

需要固定版本时，用 `https://github.com/johnsonconnor97815/frida-modified.git#v0.1.2` 作为市场来源。默认分支安装的更新命令：

```bash
claude plugin marketplace update frida-modified
claude plugin update frida-modified@frida-modified
```

在当前会话执行 `/reload-plugins` 或重启 Claude Code 后使用更新。卸载：

```bash
claude plugin uninstall frida-modified@frida-modified
claude plugin marketplace remove frida-modified
```

命令依据 [Claude Code 官方插件市场文档](https://code.claude.com/docs/en/plugin-marketplaces)。本项目用 Claude Code `2.1.273` 验证；其他版本以 `claude plugin --help` 为准。普通 Skill 的 `/frida-modified` 与插件的 `/frida-modified:frida-modified` 是两种不同安装方式的入口。

## 使用通用 skills CLI

以下命令使用 [vercel-labs/skills](https://github.com/vercel-labs/skills/tree/v1.5.26) 的固定版本 `1.5.26`，需要 Node.js **22.20.0+**（含 npm/npx）、Git 和 GitHub 网络访问；无需登录 GitHub。

## 选择 Agent 和安装范围

同时安装到 Codex 和 Claude Code，所有项目可用：

```bash
npx --yes skills@1.5.26 add johnsonconnor97815/frida-modified --skill frida-modified --agent codex claude-code --global --yes
```

`--agent` 后可以放一个或多个名称：

| Agent | 参数值 |
| --- | --- |
| Codex | `codex` |
| Claude Code | `claude-code` |
| Cursor | `cursor` |
| Gemini CLI | `gemini-cli` |
| GitHub Copilot | `github-copilot` |
| OpenCode | `opencode` |

其他 Agent 可从 [CLI 支持列表](https://github.com/vercel-labs/skills#supported-agents) 选择；本仓库的安装测试覆盖上表 6 项。

只供当前项目使用时，在项目根目录执行，不带 `--global`：

```bash
npx --yes skills@1.5.26 add johnsonconnor97815/frida-modified --skill frida-modified --agent codex claude-code --yes
```

默认使用共享副本和目录链接。Windows 或不便使用链接的环境，可以在上述安装命令末尾加 `--copy`。这仅改变安装方式；Frida 构建适配器仍针对 Linux x86_64，Windows 上执行设备脚本需要 WSL/Linux。

需要交互选择 Agent、范围和复制方式时：

```bash
npx --yes skills@1.5.26 add johnsonconnor97815/frida-modified --skill frida-modified
```

其中 `npx --yes` 接受下载 CLI；安装参数末尾的 `--yes` 才负责跳过 Skill 安装确认。

## 安装路径与旧版迁移

当前已验证的 CLI 将 Codex、Cursor、Gemini CLI、GitHub Copilot 和 OpenCode 安装到共享的 `.agents/skills/frida-modified`。全局路径位于用户目录，项目路径位于执行命令的目录。Claude Code 使用 `.claude/skills/frida-modified`，默认链接到共享副本；`--copy` 则创建独立副本。自定义 `CLAUDE_CONFIG_DIR` 时，全局 Claude Code 路径随该配置调整。

Codex 路径依据 [官方 Skill 文档](https://developers.openai.com/codex/skills)，Claude Code 路径与调用方式依据 [官方 Skill 文档](https://code.claude.com/docs/en/skills)。安装后的脚本路径以实际 `SKILL.md` 所在目录为准。

本项目 `v0.1.0` 曾指导将源码目录手动链接到 `${CODEX_HOME:-$HOME/.codex}/skills/frida-modified`。迁移到新安装方式前，先保存旧目录内的自行修改。如果该入口确实是软链，可只移除该链接，再执行一键安装；保留其指向的源码目录。若是普通目录，先将其移到备份位置。这样可避免新旧同名 Skill 同时出现。

一键安装的 `--yes` 会允许替换同名安装内容；任务日志、APK 和构建产物应保存在使用者工作目录，不应写入 Skill 安装目录。

## 固定版本、更新和卸载

默认分支适合跟进后续修复。需要固定本次发布内容时，使用 tag URL：

```bash
npx --yes skills@1.5.26 add https://github.com/johnsonconnor97815/frida-modified/tree/v0.1.2/skills/frida-modified --skill frida-modified --agent codex claude-code --global --yes
```

查看安装结果：

```bash
npx --yes skills@1.5.26 list --global
```

更新这个 Skill：

```bash
npx --yes skills@1.5.26 update frida-modified --global --yes
```

固定 tag 的安装继续跟随该 tag；切换到新版本时，重新执行目标 tag 的安装命令。需要重新选择 Agent 时，也重新运行相应安装命令。

从所有 Agent 卸载这个全局 Skill：

```bash
npx --yes skills@1.5.26 remove frida-modified --global --yes
```

项目级安装在原项目目录操作：查看和卸载去掉 `--global`，更新改用 `--project`。共用 `.agents/skills` 的 Agent 引用同一份内容，更新会同时生效；上述卸载命令移除所有 Agent 对这个 Skill 的安装。

## 安装验证

CI 使用真实 `skills` CLI，在 Linux、macOS、Windows 的临时项目和干净 CI 用户目录中检查项目级/全局安装；两种安装模式均检查 6 个 Agent 的资源、重复安装和卸载。所有安装文件与源码逐文件比较 SHA-256，包含补丁、许可证、脚本和引用文档。

本地复现项目级检查：

```bash
npm install --prefix .cache/install-cli --no-save --ignore-scripts --package-lock=false skills@1.5.26
python3 scripts/check_installation.py --cli .cache/install-cli/node_modules/skills/bin/cli.mjs
```

默认在临时项目安装，并在结束时清理。`--scope global` 只供设置了 `CI=true` 的一次性 CI 用户使用，且遇到已有同名安装会拒绝执行。公开仓库取包可加 `--source johnsonconnor97815/frida-modified`；该检查要求远端 Skill 与当前源码一致。

这些检查验证安装路径、资源完整性和 CLI 管理流程。它们不代表已登录每个 Agent 完成一次模型调用，也不扩展 [Frida 实机验证范围](VALIDATION.md)。

原生插件检查由 `scripts/check_native_installation.py` 执行，要求使用一次性容器或 `CI=true` 的干净 CI 用户。它会修改该测试用户的插件配置；已有同名插件或市场时拒绝执行。检查两套 CLI 的市场添加、安装、资源 SHA-256、发现 Skill、重装和卸载，不调用模型服务。命令示例：

```bash
python3 scripts/check_native_installation.py --record .cache/native-install.json
```

加 `--source johnsonconnor97815/frida-modified` 可测试公开 Git 来源；不传时使用当前仓库目录。原生插件验证不替代上述跨平台普通 Skill 安装验证。
