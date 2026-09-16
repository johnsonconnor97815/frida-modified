# frida-modified

一个按目标 Android 设备选版的 Codex Skill：识别环境、推荐候选版本、获取官方源码与产物、建立原版基线、适配修改、构建、对照验证和部署。

附带 Frida `17.18.0` 的 commit 固定补丁与 Linux x86_64 构建适配。版本选择不会默认套用最新版本；其他版本按实际源码和目标设备补充适配。当前案例来自 Pixel 3 / Android 12，Android 10 尚无本项目的实机验证。

## 安装和使用

克隆后将 Skill 目录链接到 Codex 的技能目录；若同名 Skill 已存在，先检查现有内容。

```bash
git clone https://github.com/johnsonconnor97815/frida-modified.git
cd frida-modified
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s "$PWD/skills/frida-modified" "${CODEX_HOME:-$HOME/.codex}/skills/frida-modified"
```

在新的 Codex 会话中使用：

> 使用 $frida-modified，先识别我指定的 Android 设备，根据环境推荐 Frida 版本，再规划需要修改的标识，完成构建和对照测试。

脚本要求 Python 3.10+、Git；设备操作需要 ADB，功能测试需要与目标产物匹配的 Python `frida`。构建、SDK/NDK 和 Java bridge 的条件按所选版本确定。首版构建适配器针对 Linux x86_64。

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

行为测试使用隔离文件和受控设备替身，检查版本/补丁约束、输入指纹、资源所有权、部署恢复及清理失败。实机、构建和 App 验证结果另见 [VALIDATION.md](VALIDATION.md)。单元测试通过不代表某个 Android 版本兼容。

本仓库分发 Skill、脚本、源码补丁及测试资源；使用者的 APK、设备序列号、本机路径、原始日志与运行产物保存在各自工作目录。功能正常、名称修改生效和目标 App 的检测结果分别记录。

原创 Skill、脚本和测试采用 [MIT License](LICENSE)。Frida 源码补丁沿用其上游许可，见 [NOTICE.md](NOTICE.md)。
