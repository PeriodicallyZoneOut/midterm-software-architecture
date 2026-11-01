#!/usr/bin/env python3
"""Prepare Docker and containerd settings on the project's disk filesystem."""

import json
import os
from pathlib import Path
import re
import subprocess
import tomllib

project_dir = Path(__file__).resolve().parent.parent
state_dir = project_dir / '.local-demo'
state_dir.mkdir(mode=0o700, exist_ok=True)
os.chmod(state_dir, 0o700)
runtime_dir = state_dir / 'runtime'
runtime_dir.mkdir(mode=0o700, exist_ok=True)

filesystem = subprocess.check_output(
    ['findmnt', '-n', '-o', 'FSTYPE', '-T', str(runtime_dir)], text=True
).strip()
if filesystem not in {'btrfs', 'ext4', 'xfs'}:
    raise SystemExit(f'Expected a disk filesystem for runtime data; found {filesystem!r}.')

source = Path('/etc/docker/daemon.json')
docker_config = json.loads(source.read_text()) if source.exists() else {}
if docker_config.get('storage-opts'):
    raise SystemExit('Review existing storage-opts before changing storage.')
docker_config.setdefault('features', {})['containerd-snapshotter'] = True
docker_config['storage-driver'] = 'overlayfs'
docker_config['data-root'] = str(runtime_dir / 'docker')

containerd_source = Path('/etc/containerd/config.toml')
command = ['containerd', '--config', str(containerd_source), 'config', 'dump']
if not containerd_source.exists():
    command = ['containerd', 'config', 'default']
containerd_config = subprocess.check_output(command, text=True)
# Canonical containerd output places its global root before all TOML tables.
globals_text, separator, tables = containerd_config.partition('[')
globals_text, count = re.subn(
    r'^root\s*=.*$', 'root = ' + json.dumps(str(runtime_dir / 'containerd')),
    globals_text, count=1, flags=re.MULTILINE,
)
if count != 1:
    raise SystemExit('Could not locate the global containerd root setting.')
containerd_config = globals_text + separator + tables
assert tomllib.loads(containerd_config)['root'] == str(runtime_dir / 'containerd')

docker_target = state_dir / 'docker-daemon-disk.json'
containerd_target = state_dir / 'containerd-disk.toml'
for target, content in [
    (docker_target, json.dumps(docker_config, indent=2) + '\n'),
    (containerd_target, containerd_config),
]:
    with open(target, 'w', opener=lambda path, flags: os.open(path, flags, 0o600)) as stream:
        stream.write(content)
subprocess.run(['dockerd', '--validate', '--config-file', str(docker_target)], check=True)
subprocess.run(
    ['containerd', '--config', str(containerd_target), 'config', 'dump'],
    check=True, stdout=subprocess.DEVNULL,
)
print(f'Prepared and validated: {docker_target}\nPrepared and validated: {containerd_target}')
print(f'Runtime data will use {runtime_dir} ({filesystem}).')
print('System configuration has not been changed. Existing runtime data has not been moved.')
