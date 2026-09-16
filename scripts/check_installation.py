"""Exercise the real skills CLI without running Android/device operations."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[1]
SKILL = 'frida-modified'
AGENTS = ['codex', 'claude-code', 'cursor', 'gemini-cli', 'github-copilot', 'opencode']
CLI_VERSION = '1.5.26'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def snapshot(directory):
    return {
        path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob('*'))
        if path.is_file() and '__pycache__' not in path.parts
    }


def exists(path):
    return os.path.lexists(path)


def check(args):
    cli = args.cli.resolve()
    require(cli.is_file(), f'CLI not found: {cli}')
    source_dir = REPO / 'skills' / SKILL
    expected = snapshot(source_dir)
    require('SKILL.md' in expected, 'Source skill not found')
    env = {**os.environ, 'DISABLE_TELEMETRY': '1', 'NO_COLOR': '1',
           'PYTHONDONTWRITEBYTECODE': '1'}

    def run(*arguments, cwd):
        result = subprocess.run(['node', str(cli), *arguments], cwd=cwd, env=env,
                                capture_output=True, text=True, encoding='utf-8',
                                errors='replace', timeout=120)
        require(result.returncode == 0,
                f'skills {arguments[0]} failed:\n{result.stdout}\n{result.stderr}')
        return result.stdout

    version = run('--version', cwd=REPO).strip()
    require(version == CLI_VERSION, f'Expected skills {CLI_VERSION}, got {version}')
    results = []
    for mode in ['symlink', 'copy']:
        with tempfile.TemporaryDirectory(prefix='frida-skill-install-') as temporary:
            project = Path(temporary)
            base = Path.home() if args.scope == 'global' else project
            canonical = base / '.agents/skills' / SKILL
            claude_base = (Path(os.environ.get('CLAUDE_CONFIG_DIR') or base / '.claude')
                           if args.scope == 'global' else base / '.claude')
            claude = claude_base / 'skills' / SKILL
            destinations = [canonical, claude]
            if args.scope == 'global':
                require(os.environ.get('CI') == 'true',
                        'Global checks require a disposable CI account with CI=true')
                config = Path(os.environ.get('XDG_CONFIG_HOME') or base / '.config')
                legacy = [Path(os.environ.get('CODEX_HOME') or base / '.codex') / 'skills' / SKILL,
                          base / '.cursor/skills' / SKILL, base / '.gemini/skills' / SKILL,
                          base / '.copilot/skills' / SKILL, config / 'opencode/skills' / SKILL]
                require(not any(exists(p) for p in destinations + legacy),
                        'Refusing global checks: an existing installation would be affected')
            scope_flags = ['--global'] if args.scope == 'global' else []
            add = ['add', args.source, '--skill', SKILL, '--agent', *AGENTS,
                   '--yes', *scope_flags, *(['--copy'] if mode == 'copy' else [])]
            installed = False
            try:
                listed = run('add', args.source, '--list', '--yes', cwd=project)
                require(SKILL in listed, 'Repository skill discovery failed')
                # Set before invoking add so a partially failed global install is cleaned up.
                installed = True
                for attempt in range(2):
                    run(*add, cwd=project)
                    for destination in destinations:
                        actual = snapshot(destination)
                        require(actual == expected,
                                f'Incomplete/different payload at {destination}; '
                                f'missing={sorted(expected.keys() - actual.keys())}, '
                                f'extra={sorted(actual.keys() - expected.keys())}, '
                                f'changed={sorted(k for k in actual.keys() & expected.keys() if actual[k] != expected[k])}')
                    print(f'{args.scope}/{mode}: install {attempt + 1}, '
                          f'{len(expected)} files verified for {len(AGENTS)} agents', flush=True)
                if mode == 'copy':
                    require(not claude.is_symlink(), 'Copy mode created a symlink')
                    if hasattr(claude, 'is_junction'):
                        require(not claude.is_junction(), 'Copy mode created a junction')
                    require(not canonical.samefile(claude), 'Copy mode did not create independent directories')
                elif os.name != 'nt':
                    require(claude.is_symlink() and canonical.samefile(claude),
                            'Default mode did not link Claude to the shared skill')
                listing = run('list', *scope_flags, cwd=project)
                require(SKILL in listing, 'Installed skill missing from list')
                for path in canonical.glob('scripts/*.py'):
                    compile(path.read_bytes(), str(path), 'exec')
                if os.name != 'nt':
                    helper = subprocess.run([sys.executable, str(claude / 'scripts/fetch.py'), '--help'],
                                            cwd=project, env=env, capture_output=True,
                                            text=True, timeout=30)
                    require(helper.returncode == 0, f'Installed helper failed: {helper.stderr}')
                results.append({'scope': args.scope, 'mode': mode, 'agents': AGENTS,
                                'files_per_destination': len(expected),
                                'discovery': True, 'install': True, 'reinstall': True,
                                'payload_hashes': True, 'list': True,
                                'helper_help': os.name != 'nt'})
            finally:
                if installed:
                    # The project is temporary, or global scope has passed the clean CI preflight.
                    # Remove all references to this one skill, including universal agents.
                    run('remove', SKILL, '--yes', *scope_flags, cwd=project)
                    require(not any(exists(p) for p in destinations), 'Uninstall left skill files behind')
            results[-1]['uninstall'] = True
            print(f'{args.scope}/{mode}: list and uninstall passed', flush=True)
    require(snapshot(source_dir) == expected, 'Installation modified the source skill')
    return {'verified_at_utc': datetime.now(timezone.utc).isoformat(),
            'skills_cli': version, 'platform': sys.platform, 'results': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cli', type=Path, required=True, help='Path to skills/bin/cli.mjs')
    parser.add_argument('--scope', choices=['project', 'global'], default='project')
    parser.add_argument('--source', default=str(REPO), help='Local repo or public GitHub source')
    parser.add_argument('--record', type=Path)
    args = parser.parse_args()
    record = check(args)
    if args.record:
        args.record.parent.mkdir(parents=True, exist_ok=True)
        args.record.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
