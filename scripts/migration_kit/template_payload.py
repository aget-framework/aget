"""Shared payload policy, shipped inside the standalone migration kit."""
import os
from pathlib import PurePosixPath
import subprocess


def is_compiled_cache(path):
    """Match cache directories and bytecode at any depth, including macOS casing."""
    path = str(path).lower()
    return '__pycache__' in PurePosixPath(path).parts or path.endswith(('.pyc', '.pyo'))


class PayloadInspectionError(ValueError):
    """A release tree could not be inspected; this must never count as clean."""


def compiled_caches_at(repo, revision):
    """Read the committed subtree under repo at revision, never a diff or working tree.

    The fleet gate supplies each template root and reads its complete tree at the tag.
    The pre-tag gate supplies its working directory or --cwd and reads only that subtree.
    """
    try:
        result = subprocess.run(
            ['git', '--no-optional-locks', '--no-lazy-fetch', '-C', str(repo),
             'ls-tree', '-r', '--name-only', '-z', revision, '--'],
            capture_output=True, stdin=subprocess.DEVNULL, timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise PayloadInspectionError(f'{repo}@{revision}: release tree unavailable: {exc}') from exc
    if result.returncode:
        raise PayloadInspectionError(
            f'{repo}@{revision}: release tree unavailable (git exit {result.returncode})')
    return sorted(os.fsdecode(p) for p in result.stdout.split(b'\0') if p and is_compiled_cache(os.fsdecode(p)))
