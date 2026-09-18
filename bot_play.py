"""Automated bot that plays Neon Crawler and reports results."""

import subprocess
import sys


def bot_play(seed=None):
    proc = subprocess.run(
        [sys.executable, 'main.py', '--bot', '--silent', f'--seed={seed or 0}', '--max-turns=2000'],
        text=True,
        capture_output=True,
        timeout=120,
    )

    print('Return code:', proc.returncode)
    if proc.stdout:
        lines = proc.stdout.splitlines()
        print('\n'.join(lines[-50:]))
    if proc.stderr:
        print('STDERR:')
        print(proc.stderr[-2000:])


if __name__ == '__main__':
    bot_play(seed=42)
