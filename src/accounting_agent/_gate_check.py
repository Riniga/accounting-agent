"""DELIBERATELY INSECURE — throwaway code on branch ci/gate-check, never merged.

Exists only to prove that the SAST gates stop insecure code (MVP-001 plan, step 4.2).
"""

import subprocess

import yaml

password = "hunter2-not-a-real-secret-9f8e7d6c5b4a"


def run_command(command: str) -> int:
    """Run a shell command (command injection)."""
    return subprocess.call(command, shell=True)


def load_untrusted(text: str) -> object:
    """Load YAML with the full loader (arbitrary object construction)."""
    return yaml.load(text, Loader=yaml.Loader)


def evaluate(expression: str) -> object:
    """Evaluate untrusted input (code injection)."""
    return eval(expression)
