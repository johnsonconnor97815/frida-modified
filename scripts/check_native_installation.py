"""Test native plugin installation in a disposable CI account (no model calls)."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

REPO = Path(__file__).resolve().parents[1]
NAME = 'frida-modified'
PLUGIN = f'{NAME}@{NAME}'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def snapshot(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*'))
            if p.is_file() and '__pycache__' not in p.parts}


def check(args):
    require(os.environ.get('CI') == 'true', 'Run only in a disposable container or CI account with CI=true')
    expected = snapshot(REPO / 'skills' / NAME)
    versions = {}
    checks = {}
    log = []
    with tempfile.TemporaryDirectory(prefix='frida-native-install-') as temporary:
        cwd = Path(temporary)

        def run(*command):
            result = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                                    encoding='utf-8', errors='replace', timeout=180)
            log.append({'command': list(command), 'exit_code': result.returncode,
                        'stdout': result.stdout, 'stderr': result.stderr})
            if args.log:
                args.log.parent.mkdir(parents=True, exist_ok=True)
                args.log.write_text(json.dumps(log, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            require(result.returncode == 0,
                    f'{command!r} failed:\n{result.stdout}\n{result.stderr}')
            return result.stdout

        for cli in ['codex', 'claude']:
            versions[cli] = run(cli, '--version').strip()
            configured = run(cli, 'plugin', 'marketplace', 'list', '--json')
            installed = run(cli, 'plugin', 'list', '--json')
            require(NAME not in configured and NAME not in installed,
                    f'Refusing to alter existing {cli} marketplace or plugin')

        for cli, install, uninstall in [('codex', 'add', 'remove'), ('claude', 'install', 'uninstall')]:
            added = False
            installed = False
            primary_error = None
            cleanup_errors = []
            try:
                run(cli, 'plugin', 'marketplace', 'add', args.source)
                added = True
                for attempt in range(2):
                    installed = True
                    run(cli, 'plugin', install, PLUGIN)
                    listing = run(cli, 'plugin', 'list', '--json')
                    require(NAME in listing, f'{cli} did not list installed plugin')
                    if cli == 'codex':
                        entry = next(p for p in json.loads(listing)['installed'] if p['pluginId'] == PLUGIN)
                        require(entry['enabled'] is True, 'Codex installed plugin is disabled')
                    config = (Path(os.environ.get('CODEX_HOME') or Path.home() / '.codex')
                              if cli == 'codex'
                              else Path(os.environ.get('CLAUDE_CONFIG_DIR') or Path.home() / '.claude'))
                    payloads = list((config / 'plugins/cache').glob(f'**/skills/{NAME}/SKILL.md'))
                    require(payloads, f'{cli} did not cache the skill')
                    for path in payloads:
                        require(snapshot(path.parent) == expected, f'{cli} installed a different/incomplete payload at {path.parent}')
                    print(f'{cli}: install {attempt + 1}, {len(expected)} skill files verified', flush=True)
                if cli == 'claude':
                    inventory = run('claude', 'plugin', 'details', PLUGIN)
                    require(NAME in inventory and 'skill' in inventory.lower(), 'Claude did not discover plugin skill')
                refresh = 'upgrade' if cli == 'codex' else 'update'
                run(cli, 'plugin', 'marketplace', refresh, NAME)
                run(cli, 'plugin', 'add' if cli == 'codex' else 'update', PLUGIN)
                for path in payloads:
                    require(snapshot(path.parent) == expected, f'{cli} update changed skill payload')
                checks[cli] = {'update': True, 'marketplace': True, 'install': True, 'reinstall': True,
                               'listed': True, 'files_verified': len(expected)}
            except Exception as error:
                primary_error = error
            finally:
                if installed:
                    try:
                        run(cli, 'plugin', uninstall, PLUGIN)
                        remaining = run(cli, 'plugin', 'list', '--json')
                        require(PLUGIN not in remaining, f'{cli} still lists the removed plugin')
                    except Exception as error:
                        cleanup_errors.append(str(error))
                if added:
                    try:
                        run(cli, 'plugin', 'marketplace', 'remove', NAME)
                    except Exception as error:
                        cleanup_errors.append(str(error))
            if primary_error or cleanup_errors:
                raise RuntimeError(f'Primary error: {primary_error}; cleanup errors: {cleanup_errors}') from primary_error
            checks[cli]['uninstall'] = True
            print(f'{cli}: list and uninstall passed', flush=True)
    require(snapshot(REPO / 'skills' / NAME) == expected, 'Native install changed source Skill')
    return {'verified_at_utc': datetime.now(timezone.utc).isoformat(),
            'source': args.source, 'versions': versions, 'checks': checks,
            'model_calls': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', default=str(REPO))
    parser.add_argument('--record', type=Path)
    parser.add_argument('--log', type=Path)
    args = parser.parse_args()
    record = check(args)
    if args.record:
        args.record.parent.mkdir(parents=True, exist_ok=True)
        args.record.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
