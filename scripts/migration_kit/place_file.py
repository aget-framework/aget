#!/usr/bin/env python3
"""PLACER (R1 clause 7): place one release file into a member at the act, never through a link. Replaces the session's
`cp -f <staged> <path>` and `mkdir -p <folder>`. Self-contained (standard library only), because it is copied into the
packet's sealed stage and its digest is in the stage manifest; the session runs that sealed copy, exactly as declared.

Usage: python3 <packet root>/stage/kit/place_file.py <member> <path> <staged> <sha256>

Refuses (exit 2, nothing written) unless: the current folder is <member>; <path> is a plain relative path; the staged
file's bytes have <sha256>; every folder from <member> to the target's parent is reached with O_NOFOLLOW (missing ones
are made with mkdirat at their parent's fd), and is reached again, by a fresh walk, immediately before each mkdir and
before the rename; the target is absent or a regular file with one name. The bytes go to a new temp file in that
folder (O_CREAT|O_EXCL|O_NOFOLLOW), are read back, and are renamed onto the name: never an in-place truncation.
Stated limit, as for the kit's own writer: this holds under exclusive mutation of the member's folder tree; a folder
moved by another process after the last re-walk is not seen.
"""
import hashlib
import os
import secrets
import stat
import sys


class Refused(Exception):
    pass


class Missing(Refused):
    """A folder on the path does not exist (as against one that is a link or not a folder)."""


def _root(root):
    """B193 finding 1 (shared by every reader and writer here): the member folder named so that O_NOFOLLOW applies to
    the member itself: no NUL, no trailing slash (`<link>/` opens the target), no `.` or `..` name (`<link>/./`,
    `<link>/sub/../` open through the link). Folders above the member are the operator's and are not walked."""
    r = str(root)
    if "\0" in r:
        raise Refused("the member's path holds a NUL byte")
    r = r.rstrip("/") or "/"
    if any(c in (".", "..") for c in r.split("/")):
        raise Refused(f"{r}: a member folder named with `.` or `..`")
    return r


def _walk(root, comps, create=False):
    try:
        fd = os.open(_root(root), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as e:                         # the member folder itself: a link, not a folder, or not there
        raise Refused(f"{root}: cannot be opened without following a link ({e.strerror or e})") from None
    done = []
    try:
        for c in comps:
            try:
                st = os.stat(c, dir_fd=fd, follow_symlinks=False)
            except FileNotFoundError:
                if not create:
                    raise Missing(f"{'/'.join(done + [c])} does not exist") from None
                _same(root, done, fd)
                os.mkdir(c, 0o777, dir_fd=fd)
                st = os.stat(c, dir_fd=fd, follow_symlinks=False)
            if not stat.S_ISDIR(st.st_mode):
                raise Refused(f"{'/'.join(done + [c])} is a symbolic link or not a folder")
            try:
                nfd = os.open(c, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            except OSError as e:
                raise Refused(f"{'/'.join(done + [c])} cannot be opened without following a link ({e})") from None
            os.close(fd)
            fd = nfd
            done.append(c)
        return fd
    except BaseException:
        os.close(fd)
        raise


def _same(root, comps, pfd):
    fd = _walk(root, comps)
    try:
        a, b = os.fstat(fd), os.fstat(pfd)
        if (a.st_dev, a.st_ino) != (b.st_dev, b.st_ino):
            raise Refused(f"{'/'.join(comps) or '.'} was moved or replaced after it was opened")
    finally:
        os.close(fd)


def read_entry(root, rel):
    """E2i15 (FWK-OVSR6's E2i14 pre-read 1-3, reproduced): the working-tree entry at `rel` under `root`, reached with
    no link followed ANYWHERE on its path, as `place` reaches a target: every folder from `root` down is opened with
    O_NOFOLLOW at its parent's fd. Returns ("file", bytes), ("absent", None) when the entry or a folder above it does
    not exist, ("link", target) for a link at the leaf, or ("other", mode) for any other leaf. A folder on the path
    that is a link (dangling or not) or not a folder raises Refused: it is never read through and never absent."""
    if "\0" in str(rel) or "\0" in str(root):     # E2i16 (FWK-OVSR6's E2i15 pre-read 2): refused, never a crash
        raise Refused("a path holds a NUL byte")
    comps = str(rel).split("/")
    if str(rel).startswith("/") or any(c in ("", "..", ".") for c in comps):
        raise Refused(f"{rel}: not a plain relative path")
    root = _root(root)                   # E2i16/C2a10/B193 finding 1: the member named without `/`, `.`, `..`
    try:
        pfd = _walk(root, comps[:-1])
    except Missing:
        return "absent", None
    except Refused:
        raise
    except OSError as e:                         # the member folder itself: a link, not a folder, or not there
        raise Refused(f"{root}: cannot be opened without following a link ({e.strerror or e})") from None
    try:
        try:
            st = os.stat(comps[-1], dir_fd=pfd, follow_symlinks=False)
        except FileNotFoundError:
            return "absent", None
        if stat.S_ISLNK(st.st_mode):
            return "link", os.readlink(comps[-1], dir_fd=pfd)
        if not stat.S_ISREG(st.st_mode):
            return "other", stat.S_IFMT(st.st_mode)
        fd = os.open(comps[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=pfd)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                return "other", stat.S_IFMT(os.fstat(fd).st_mode)
            chunks = []
            while chunk := os.read(fd, 1 << 20):
                chunks.append(chunk)
            return "file", b"".join(chunks)
        finally:
            os.close(fd)
    finally:
        os.close(pfd)


def place(member, rel, staged, want):
    """Place the digest-checked staged bytes without following destination links, carrying the release executable bit."""
    if not os.path.samefile(os.getcwd(), member):
        raise Refused(f"run this in {member}, not {os.getcwd()}")
    comps = rel.split("/")
    if not rel or os.path.isabs(rel) or any(c in ("", ".", "..") for c in comps):
        raise Refused(f"{rel} is not a plain relative path")
    with open(staged, "rb") as fh:
        data = fh.read()
        mode = 0o755 if os.fstat(fh.fileno()).st_mode & stat.S_IXUSR else 0o644
    if hashlib.sha256(data).hexdigest() != want:
        raise Refused(f"the staged file {staged} does not have the digest {want[:12]}")
    pfd = _walk(member, comps[:-1], create=True)
    leaf, tmp = comps[-1], None
    try:
        try:
            st = os.stat(leaf, dir_fd=pfd, follow_symlinks=False)
        except FileNotFoundError:
            st = None
        if st is not None and (not stat.S_ISREG(st.st_mode) or st.st_nlink != 1):
            raise Refused(f"{rel} is not a regular file with one name")
        _same(member, comps[:-1], pfd)
        tmp = f".{leaf}.place-{os.getpid()}-{secrets.token_hex(4)}.tmp"
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o666, dir_fd=pfd)
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            if mode is not None:
                os.fchmod(fh.fileno(), mode)
        rfd = os.open(tmp, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=pfd)
        with os.fdopen(rfd, "rb") as fh:
            if fh.read() != data:
                raise Refused(f"the temp file for {rel} did not read back")
        _same(member, comps[:-1], pfd)
        os.rename(tmp, leaf, src_dir_fd=pfd, dst_dir_fd=pfd)
        tmp = None
    finally:
        if tmp is not None:
            try:
                os.unlink(tmp, dir_fd=pfd)
            except OSError:
                pass
        os.close(pfd)


def main(argv=None):
    """Place one sealed release file from four CLI arguments; return 2 on a refused or invalid request."""
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 4:
        print("usage: place_file.py <member> <path> <staged> <sha256>", file=sys.stderr)
        return 2
    try:
        place(*argv)
    except (Refused, OSError, ValueError) as e:      # C2a11 (LOW): a NUL in an argument is a refusal, not a crash
        print(f"REFUSED: {e}; nothing was written", file=sys.stderr)
        return 2
    print(f"placed {argv[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
