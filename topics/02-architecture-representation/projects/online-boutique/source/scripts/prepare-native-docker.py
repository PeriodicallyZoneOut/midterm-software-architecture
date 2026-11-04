#!/usr/bin/env python3
"""Prepare and validate a Docker native-snapshotter config without applying it."""

import json
import os
from pathlib import Path
import subprocess

project_dir = Path(__file__).resolve().parent.parent
source = Path('/etc/docker/daemon.json')
config = json.loads(source.read_text()) if source.exists() else {}
if config.get('storage-opts'):
    raise SystemExit('Review existing storage-opts before changing the snapshotter.')

config.setdefault('features', {})['containerd-snapshotter'] = True
config['storage-driver'] = 'native'
state_dir = project_dir / '.local-demo'
state_dir.mkdir(mode=0o700, exist_ok=True)
os.chmod(state_dir, 0o700)
target = state_dir / 'docker-daemon-native.json'
with open(target, 'w', opener=lambda path, flags: os.open(path, flags, 0o600)) as stream:
    json.dump(config, stream, indent=2)
    stream.write('\n')
subprocess.run(['dockerd', '--validate', '--config-file', str(target)], check=True)
print(f'Prepared: {target}')
print('System configuration has not been changed.')
