#!/usr/bin/env python3
"""Watch a receiver's Claude Code settings files for permission-rule changes DURING a session.

WHY. On 2026-09-26 a before/after comparison of a pilot Aget's settings reported "no new rule"
while the session had created five standing rules and removed them on three principal rulings. A
comparison of two endpoints measures a net state, and a net of zero is not an absence of events. This
polls every file every second and logs each rule-set change as it happens.

Output is aggregate-only: per change, the time, which file (by role), and counts plus short digests of
rules added and removed. Rule text is never written, so the log is safe for a private receiver.

COVERAGE (the settings-watch coverage check, 2026-09-26). The first version summarized an EMPTY log, and a killed watch with no
stop event, to exit 0 "no rule change observed". Silence is not evidence. The watch now declares its poll
interval and heartbeat, writes a heartbeat event every `heartbeat` seconds, and stamps every event with an
epoch `t`. The summary gives one verdict:
    FAIL          at least one rule-set change was observed (a change later reversed still fails);
    INCONCLUSIVE  no FAIL, but coverage is not shown: no events, no start, no stop, a legacy log with no
                  declared heartbeat, a gap between events longer than the heartbeat allows, a settings file
                  unreadable at start or on change, or a --window the watch does not cover; OR (G2.5,
                  2026-09-27) a settings file was written with no visible rule change (`write` event), or the
                  log does not declare stat tracking — either way a rule added and removed between two polls
                  cannot be excluded;
    PASS          none of the above.

Files: the four settings files, plus ~/.claude.json's `projects[<root>].allowedTools` (content only — Claude
Code rewrites that file for unrelated state, so its stat is not tracked). SIGTERM or SIGINT ends the watch
with a stop event (`by: signal`), so the operator can end it when the receiver session exits.

Usage:
    watch_settings_rules.py --root <receiver-root> --log <out.jsonl> [--interval 1] [--heartbeat 10] [--duration SECONDS]
    watch_settings_rules.py --summarize <out.jsonl> [--window-start EPOCH --window-end EPOCH]
Exit (summarize): 0 = PASS, 1 = FAIL, 2 = log unreadable, 3 = INCONCLUSIVE.
"""
import argparse
import datetime
import hashlib
import json
import os
import stat
import signal
import sys
import time

KINDS = ('allow', 'deny', 'ask', 'additionalDirectories')
# G2.5 (2026-09-27). A rule added and removed between two polls leaves identical content at both, so the
# content diff cannot see it. The file's stat signature still moves; a moved signature with no rule change
# is a `write` event, and any write makes the verdict INCONCLUSIVE. ~/.claude.json is excluded: Claude Code
# rewrites it for unrelated session state, so its signature says nothing; only its per-project
# `allowedTools` content is watched there.
STAT_TRACKED = ('project', 'project_local', 'user', 'user_local')
EXIT_PASS, EXIT_FAIL, EXIT_UNREADABLE, EXIT_INCONCLUSIVE = 0, 1, 2, 3
# Timestamps come from a sleeping loop; allow scheduling slack on top of the declared heartbeat.
GAP_SLACK_S = 2.0


def files_for(root):
    """Return the five settings-file paths inspected by this watcher, keyed by role."""
    return {'project': os.path.join(root, '.claude/settings.json'),
            'project_local': os.path.join(root, '.claude/settings.local.json'),
            'user': os.path.expanduser('~/.claude/settings.json'),
            'user_local': os.path.expanduser('~/.claude/settings.local.json'),
            'user_legacy': os.path.expanduser('~/.claude.json')}


def stat_sig(path):
    """Return the file's modification time, size and inode, or None when it cannot be read."""
    try:
        st = os.stat(path)
    except OSError:
        return None
    return (st.st_mtime_ns, st.st_size, st.st_ino)


def rules(path, root=None):
    """Set of short digests of every permission rule in the file; None if absent; 'UNREADABLE' on error.
    For ~/.claude.json, only `projects[root].allowedTools` counts."""
    # C2a12 (FWK-OVSR6's C2a12 pre-read): only a missing file is absent; a stat that fails otherwise (EACCES on a
    # parent folder read as absent, a false rule removal) is UNREADABLE. A non-regular file is UNREADABLE and is never
    # opened for a blocking read (a FIFO hung the watch); the file is opened non-blocking and checked again by fstat
    try:
        st = os.stat(path)
    except FileNotFoundError:
        return None
    except OSError:
        return 'UNREADABLE'
    if not stat.S_ISREG(st.st_mode):
        return 'UNREADABLE'
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                return 'UNREADABLE'
            with os.fdopen(fd, 'rb') as fh:
                fd = None
                data = json.loads(fh.read())
        finally:
            if fd is not None:
                os.close(fd)
    except (OSError, ValueError):
        return 'UNREADABLE'
    if not isinstance(data, dict):
        return 'UNREADABLE'
    if path.endswith('.claude.json'):
        allowed = ((data.get('projects') or {}).get(root) or {}).get('allowedTools') or []
        return {hashlib.sha256(('allowedTools:' + r).encode()).hexdigest()[:16] for r in allowed}
    perms = data.get('permissions') or {}
    mode = perms.get('defaultMode')
    out = {hashlib.sha256((k + ':' + r).encode()).hexdigest()[:16] for k in KINDS for r in (perms.get(k) or [])}
    if mode:
        out.add('defaultMode:' + hashlib.sha256(str(mode).encode()).hexdigest()[:8])
    return out


def now():
    """Return the current local time as an ISO 8601 string with its offset."""
    return datetime.datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S%z')


def _emit(fh, event):
    event.setdefault('at', now())
    event.setdefault('t', time.time())
    fh.write(json.dumps(event) + '\n')
    fh.flush()


def watch(root, log, interval, duration, heartbeat=10.0):
    """Poll the enumerated settings files and append observed changes until the duration ends or a signal stops the watch."""
    paths = files_for(root)
    state = {k: rules(p, root) for k, p in paths.items()}
    sigs = {k: stat_sig(paths[k]) for k in STAT_TRACKED}
    with open(log, 'a') as fh:
        _emit(fh, {'event': 'start', 'root_digest': hashlib.sha256(root.encode()).hexdigest()[:12],
                   'interval': interval, 'heartbeat': heartbeat, 'stat_tracked': sorted(STAT_TRACKED),
                   'files': {k: (None if v is None else ('UNREADABLE' if v == 'UNREADABLE' else len(v)))
                             for k, v in state.items()}})
        end = time.time() + duration if duration else None
        try:
            _loop(fh, paths, root, state, sigs, interval, end, heartbeat)
        except KeyboardInterrupt:          # SIGINT, or SIGTERM via main(): the operator ended the watch
            _emit(fh, {'event': 'stop', 'by': 'signal'})
            return
        _emit(fh, {'event': 'stop'})


def _loop(fh, paths, root, state, sigs, interval, end, heartbeat):
    last_beat = time.time()
    # C2a12 (FWK-OVSR6's C2a11 pre-read 6): a reading not taken is not a rule change. A file that turns unreadable is
    # reported as such (readable False); when it reads again it is compared with its LAST READABLE rule set, so a rule
    # added while it was unreadable is still a change, and one that comes back unchanged is not
    seen = {k: v for k, v in state.items() if v != 'UNREADABLE'}
    while end is None or time.time() < end:
        time.sleep(interval)
        for k, p in paths.items():
            cur = rules(p, root)
            sig = stat_sig(p) if k in sigs else None
            if cur != state[k]:
                if cur == 'UNREADABLE' or k not in seen:
                    _emit(fh, {'event': 'change', 'file': k, 'added': [], 'removed': [],
                               'readable': cur != 'UNREADABLE', 'present': cur is not None, 'was_readable': False})
                elif cur != seen[k]:
                    before = seen[k] if isinstance(seen[k], set) else set()
                    after = cur if isinstance(cur, set) else set()
                    _emit(fh, {'event': 'change', 'file': k,
                               'added': sorted(after - before), 'removed': sorted(before - after),
                               'readable': True, 'present': cur is not None, 'was_readable': True})
                if cur != 'UNREADABLE':
                    seen[k] = cur
                state[k] = cur
            elif k in sigs and sig != sigs[k]:
                _emit(fh, {'event': 'write', 'file': k})
            if k in sigs:
                sigs[k] = sig
        if time.time() - last_beat >= heartbeat:
            _emit(fh, {'event': 'heartbeat'})
            last_beat = time.time()


def verdict(events, window=None):
    """PASS / FAIL / INCONCLUSIVE with reasons. FAIL outranks INCONCLUSIVE: an observed change is proof.
    `between_poll` repeats, separately, the reasons that are only between-poll uncertainty (a write with no visible
    rule change; no stat tracking), so a caller can treat them apart from coverage gaps (gh#2802, 2026-09-28)."""
    reasons, between_poll = [], []
    changes = [e for e in events if e.get('event') == 'change']
    # C2a12 (FWK-OVSR6's C2a11 pre-read 6): a change to or from an unreadable file is a reading not taken, not an
    # observed rule change: INCONCLUSIVE, unless a readable-to-readable change also shows (FAIL outranks)
    unread = [e for e in changes if e.get('readable') is False or e.get('was_readable') is False]
    changes = [e for e in changes if e not in unread]
    if unread:
        reasons.append(f"{len(unread)} settings file reading(s) not taken during the watch "
                       f"({', '.join(sorted({str(e.get('file')) for e in unread}))})")
    if changes:
        return {'verdict': 'FAIL', 'changes': len(changes),
                'reasons': [f'{len(changes)} rule-set change(s) observed'], 'between_poll': []}
    starts = [e for e in events if e.get('event') == 'start']
    stops = [e for e in events if e.get('event') == 'stop']
    if not events:
        reasons.append('no events: an empty log shows nothing was watched')
    if not starts:
        reasons.append('no start event')
    if not stops:
        reasons.append('no stop event: the watch was killed or is still running; its end is unseen')
    if starts:
        s = starts[0]
        hb = s.get('heartbeat')
        if hb is None or 't' not in s:
            reasons.append('no declared heartbeat or epoch stamps (legacy log): coverage cannot be shown')
        else:
            allowed = float(hb) + max(2 * float(s.get('interval') or 0), GAP_SLACK_S)
            stamps = [e['t'] for e in events if 't' in e]
            gaps = [b - a for a, b in zip(stamps, stamps[1:]) if b - a > allowed]
            if gaps:
                reasons.append(f'{len(gaps)} gap(s) longer than {allowed:.1f}s (largest {max(gaps):.1f}s)')
            if window and stops and 't' in stops[-1]:
                if s['t'] > window[0] or stops[-1]['t'] < window[1]:
                    reasons.append('the watch does not cover the requested window')
            elif window:
                reasons.append('window requested but the watch has no stamped stop')
        if any(v == 'UNREADABLE' for v in (s.get('files') or {}).values()):
            reasons.append('a settings file was unreadable at start')
        if 'stat_tracked' not in s:
            between_poll.append('writes between polls were not stat-tracked: a rule added and removed between two '
                                'polls cannot be excluded')
    writes = [e for e in events if e.get('event') == 'write']
    if writes:
        between_poll.append(f'{len(writes)} write(s) with no visible rule change: a rule added and removed '
                            f'between polls cannot be excluded ({", ".join(sorted({e["file"] for e in writes}))})')
    reasons += between_poll
    return {'verdict': 'INCONCLUSIVE' if reasons else 'PASS', 'changes': 0, 'reasons': reasons,
            'between_poll': between_poll}


def summarize(log, window=None):
    """Print the changes recorded in a watch log and return the exit code for its verdict."""
    try:
        events = [json.loads(ln) for ln in open(log) if ln.strip()]
    except (OSError, ValueError) as exc:
        print(f'log unreadable: {exc}')
        return EXIT_UNREADABLE
    changes = [e for e in events if e.get('event') == 'change']
    starts = [e['at'] for e in events if e.get('event') == 'start']
    print('watch started', starts[0] if starts else 'UNKNOWN', '| rule-set changes observed:', len(changes))
    for e in changes:
        print('  %s %s: +%d -%d%s' % (e['at'], e['file'], len(e['added']), len(e['removed']),
                                      '' if e['readable'] else ' (unreadable)'))
    v = verdict(events, window)
    print('verdict:', v['verdict'], *(f'\n  - {r}' for r in v['reasons']))
    return {'PASS': EXIT_PASS, 'FAIL': EXIT_FAIL, 'INCONCLUSIVE': EXIT_INCONCLUSIVE}[v['verdict']]


def main():
    """Command-line entry point: watch a root's settings files, or summarize an existing watch log."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root')
    ap.add_argument('--log')
    ap.add_argument('--interval', type=float, default=1.0)
    ap.add_argument('--duration', type=float, default=0)
    ap.add_argument('--heartbeat', type=float, default=10.0)
    ap.add_argument('--summarize')
    ap.add_argument('--window-start', type=float)
    ap.add_argument('--window-end', type=float)
    a = ap.parse_args()
    if a.summarize:
        window = (a.window_start, a.window_end) if a.window_start is not None and a.window_end is not None else None
        return summarize(a.summarize, window)
    if not a.root or not a.log:
        ap.error('--root and --log are required unless --summarize')

    def _terminate(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, _terminate)
    watch(os.path.realpath(a.root), a.log, a.interval, a.duration, a.heartbeat)
    return 0


if __name__ == '__main__':
    sys.exit(main())
