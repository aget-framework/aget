"""Row 33: distinguish a slow health check from a broken health check."""
import importlib.util
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/wind_down.py"
spec = importlib.util.spec_from_file_location("wind_down_health_timeout", SCRIPT)
WD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(WD)


@pytest.fixture
def agent(tmp_path, monkeypatch):
    (tmp_path / ".aget").mkdir()
    (tmp_path / "scripts").mkdir()
    monkeypatch.delenv("AGET_WIND_DOWN_HEALTH_TIMEOUT", raising=False)
    # Keep global nugget scanning inside this fixture as well.
    monkeypatch.setenv("HOME", str(tmp_path))
    return tmp_path


def test_row_33_sleeping_health_check_times_out_without_failing_close(agent, monkeypatch, capsys):
    (agent / "scripts/health_check.py").write_text("import time\ntime.sleep(5)\n")
    monkeypatch.setenv("AGET_WIND_DOWN_HEALTH_TIMEOUT", "1")
    real_popen = subprocess.Popen
    requested = []

    class ObservedProcess(real_popen):
        def communicate(self, *args, **kwargs):
            if kwargs.get('timeout') is not None:
                requested.append(kwargs['timeout'])
            return super().communicate(*args, **kwargs)

    monkeypatch.setattr(WD.subprocess, "Popen", ObservedProcess)
    data = WD.get_wind_down_data(agent)
    health = data["health_check"]
    assert health["status"] == "timeout"
    assert "timeout" in health["message"].lower()
    assert "1 seconds" in health["message"]
    assert health["errors"] == 0
    assert data["clean_close"] is True
    assert requested[0] == 1
    output = WD.format_human_output(data)
    assert "Health Gate: TIMEOUT" in output
    assert health["message"] in output
    assert "ERROR" not in output
    assert "0/0" not in output

    # Exercise the second error consumer: main's exit gate.
    monkeypatch.setattr(WD, "get_wind_down_data", lambda *args, **kwargs: data)
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--dir", str(agent), "--force"])
    assert WD.main() == 0
    assert "Health Gate: TIMEOUT" in capsys.readouterr().out


@pytest.mark.parametrize("configured, expected", [
    (None, 120), ("180", 180), ("3600", 3600), ("0.25", 120),
    ("invalid", 120), ("", 120), ("0", 120), ("-1", 120),
    ("nan", 120), ("inf", 120), ("3601", 120), ("2147484", 120), ("9999999999", 120),
])
def test_row_33_health_timeout_configuration(agent, monkeypatch, capsys, configured, expected):
    (agent / "scripts/health_check.py").write_text(
        'print(\'{"status": "healthy", "summary": {"passed": 1, "total": 1}}\')\n')
    if configured is not None:
        monkeypatch.setenv("AGET_WIND_DOWN_HEALTH_TIMEOUT", configured)
    requested = []

    real_popen = subprocess.Popen

    class ObservedProcess(real_popen):
        def communicate(self, *args, **kwargs):
            requested.append(kwargs['timeout'])
            return super().communicate(*args, **kwargs)

    monkeypatch.setattr(WD.subprocess, "Popen", ObservedProcess)
    assert WD.run_health_check(agent)["status"] == "healthy"
    assert requested == [expected]
    if configured not in (None, '180', '3600'):
        note = capsys.readouterr().err
        assert 'AGET_WIND_DOWN_HEALTH_TIMEOUT' in note
        assert '120' in note


def test_row_33_real_health_failure_remains_error(agent, monkeypatch, capsys):
    report = {"status": "error", "summary": {"passed": 19, "total": 35,
                                             "warnings": 14, "errors": 2}}
    (agent / "scripts/health_check.py").write_text(
        "import sys\nprint(" + repr(json.dumps(report)) + ")\nsys.exit(2)\n")
    data = WD.get_wind_down_data(agent)
    assert data["health_check"] == {"status": "error", "checks_passed": 19,
                                    "checks_total": 35, "warnings": 14, "errors": 2,
                                    "message": ""}
    assert data["clean_close"] is False
    assert "Health Gate: ERROR (19/35 passed)" in WD.format_human_output(data)
    monkeypatch.setattr(WD, "get_wind_down_data", lambda *args, **kwargs: data)
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--dir", str(agent), "--force"])
    assert WD.main() == 2
    assert "Health Gate: ERROR (19/35 passed)" in capsys.readouterr().out


def test_row_33_execution_failure_remains_error(agent, monkeypatch):
    (agent / "scripts/health_check.py").write_text("# stub\n")

    def broken_run(*args, **kwargs):
        raise OSError("cannot execute health check")

    monkeypatch.setattr(WD.subprocess, "Popen", broken_run)
    health = WD.run_health_check(agent)
    assert health["status"] == "error"
    assert health["errors"] == 1
    assert "cannot execute health check" in health["message"]


@pytest.mark.parametrize('stdout', ['', 'not JSON'])
def test_c9_crashed_health_check_reports_error_and_exit_code(agent, monkeypatch, capsys, stdout):
    (agent / 'scripts/health_check.py').write_text(
        'import sys\n' + (f'print({stdout!r})\n' if stdout else '') +
        'sys.stderr.write("crashed\\n")\nsys.exit(7)\n')
    monkeypatch.setattr(sys, 'argv', [str(SCRIPT), '--dir', str(agent), '--force'])
    assert WD.main() == 2
    output = capsys.readouterr().out
    assert 'Health Gate: ERROR' in output
    assert 'exit code 7' in output
    assert 'Health check passed (0/0)' not in output


@pytest.mark.skipif(os.name != 'posix', reason='POSIX process groups')
def test_c9_timeout_kills_grandchild(agent, monkeypatch):
    pidfile = agent / 'grandchild.pid'
    heartbeat = agent / 'grandchild.heartbeat'
    child = ('import time\nfrom pathlib import Path\n'
             f'p = Path({str(heartbeat)!r})\n'
             'end = time.monotonic() + 30\n'
             'while time.monotonic() < end:\n'
             '    p.write_text(str(time.time_ns()))\n'
             '    time.sleep(0.05)\n')
    (agent / 'scripts/health_check.py').write_text(
        'import subprocess, sys, time\n'
        'from pathlib import Path\n'
        f'p = subprocess.Popen([sys.executable, "-c", {child!r}])\n'
        f'Path({str(pidfile)!r}).write_text(str(p.pid))\n'
        'time.sleep(30)\n')
    monkeypatch.setenv('AGET_WIND_DOWN_HEALTH_TIMEOUT', '1')
    pid = None
    try:
        started = time.monotonic()
        assert WD.run_health_check(agent)['status'] == 'timeout'
        assert time.monotonic() - started < 5
        pid = int(pidfile.read_text())
        # A heartbeat detects a live descendant without process-table access and
        # also tolerates an already killed zombie awaiting init on Linux.
        assert heartbeat.exists(), 'control: grandchild started before timeout'
        before = heartbeat.read_text()
        time.sleep(0.3)
        assert heartbeat.read_text() == before, f'grandchild {pid} still running'
    finally:
        if pid is None and pidfile.exists():
            pid = int(pidfile.read_text())
        if pid:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass


def test_c9_help_documents_timeout_contract():
    result = subprocess.run([sys.executable, str(SCRIPT), '--help'], capture_output=True, text=True)
    assert result.returncode == 0
    for text in [result.stdout, WD.__doc__]:
        assert 'TIMEOUT' in text
        assert 'AGET_WIND_DOWN_HEALTH_TIMEOUT' in text
        assert '3600' in text
        assert '120' in text


@pytest.mark.skipif(os.name != 'posix', reason='POSIX process groups')
def test_c16_timeout_eperm_remains_timeout(agent, monkeypatch, capsys):
    (agent / 'scripts/health_check.py').write_text('import time\ntime.sleep(30)\n')
    monkeypatch.setenv('AGET_WIND_DOWN_HEALTH_TIMEOUT', '1')
    killpg = os.killpg

    def gone_group(pid, sig):
        # Reproduce macOS's EPERM once only the dead leader remains, without
        # depending on the platform's zombie timing or leaving a live child.
        killpg(pid, sig)
        raise PermissionError(1, 'Operation not permitted')

    monkeypatch.setattr(WD.os, 'killpg', gone_group)
    data = WD.get_wind_down_data(agent)
    assert data['health_check']['status'] == 'timeout'
    assert data['health_check']['errors'] == 0
    assert data['clean_close'] is True
    monkeypatch.setattr(WD, 'get_wind_down_data', lambda *a, **kw: data)
    monkeypatch.setattr(sys, 'argv', [str(SCRIPT), '--dir', str(agent), '--force'])
    assert WD.main() == 0
    assert 'Health Gate: TIMEOUT' in capsys.readouterr().out


@pytest.mark.skipif(os.name != 'posix', reason='POSIX process groups')
@pytest.mark.parametrize('leader_exits', [False, True], ids=['live-leader', 'exited-leader'])
def test_c16_timeout_bounds_escaped_pipe_drain(agent, monkeypatch, leader_exits):
    pidfile = agent / 'escaped.pid'
    (agent / 'scripts/health_check.py').write_text(
        'import subprocess, sys, time\nfrom pathlib import Path\n'
        'p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(9)"], '
        'start_new_session=True)\n'
        f'Path({str(pidfile)!r}).write_text(str(p.pid))\n' +
        ('' if leader_exits else 'time.sleep(30)\n'))
    monkeypatch.setenv('AGET_WIND_DOWN_HEALTH_TIMEOUT', '1')
    try:
        started = time.monotonic()
        health = WD.run_health_check(agent)
        elapsed = time.monotonic() - started
        assert elapsed < 7.5, f'escaped pipe kept wind-down waiting for {elapsed:.2f}s'
        assert health['status'] == 'timeout'
        assert health['errors'] == 0
        assert '1 seconds' in health['message']
    finally:
        if pidfile.exists():
            try:
                os.kill(int(pidfile.read_text()), signal.SIGKILL)
            except ProcessLookupError:
                pass


@pytest.mark.parametrize('body', [
    'pass',
    'print("Traceback-ish garbage")',
    'import sys; sys.stderr.write("Traceback ...")',
    'print(\'{"status":"healthy","summary":{"passed":0,"total":0}}\')',
    'print(\'{"status":"healthy"}\')',
])
def test_c16_zero_observations_never_pass(agent, monkeypatch, capsys, body):
    (agent / 'scripts/health_check.py').write_text(body + '\n')
    health = WD.run_health_check(agent)
    assert health['status'] in ('unknown', 'error')
    assert health['checks_total'] == 0
    monkeypatch.setattr(sys, 'argv', [str(SCRIPT), '--dir', str(agent), '--force'])
    WD.main()
    output = capsys.readouterr().out
    assert 'Health check passed' not in output
    assert 'Health Gate: UNKNOWN' in output or 'Health Gate: ERROR' in output


@pytest.mark.parametrize('report, code', [
    ({'status': 'healthy', 'summary': {'passed': 33, 'total': 33}}, 1),
    ({}, 3),
    ({'status': 'warning', 'summary': {'passed': 1, 'total': 2, 'warnings': 1}}, 7),
])
def test_c16_json_cannot_hide_bad_exit(agent, monkeypatch, capsys, report, code):
    (agent / 'scripts/health_check.py').write_text(
        f'import sys\nprint({json.dumps(report)!r})\nsys.exit({code})\n')
    health = WD.run_health_check(agent)
    assert health['status'] == 'error'
    assert health['errors'] >= 1
    assert f'exit code {code}' in health['message']
    monkeypatch.setattr(sys, 'argv', [str(SCRIPT), '--dir', str(agent), '--force'])
    assert WD.main() == 2
    assert 'Health Gate: ERROR' in capsys.readouterr().out


@pytest.mark.parametrize('status, code', [('healthy', 0), ('warning', 1)])
def test_c16_matching_json_exit_preserves_report(agent, status, code):
    report = {'status': status, 'summary': {'passed': 1, 'total': 2, 'warnings': code}}
    (agent / 'scripts/health_check.py').write_text(
        f'import sys\nprint({json.dumps(report)!r})\nsys.exit({code})\n')
    health = WD.run_health_check(agent)
    assert health['status'] == status
    assert health['checks_total'] == 2
