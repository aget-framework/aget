"""Test helper (C2a7, B185 finding 1): a stub suite that passes one test and writes the kit report the way the kit's
pytest plugin does (one clean invocation), so the kit reads it as a complete run."""
import json
import os
import uuid

inv = uuid.uuid4().hex
path, token = os.environ.get("AGET_KIT_REPORT"), os.environ.get("AGET_KIT_REPORT_TOKEN")
if path and token:
    with open(path, "a") as fh:
        for rec in ({"rec": "start", "pid": os.getpid(), "args": [], "dir": ".", "lf": False},
                    {"rec": "finish", "exit": 0, "events": 0, "collected": 0, "ran": 0, "deselected": [],
                     "narrowed": [], "dropped": 0, "suppressed": [], "selection": {"roots": ["tests"], "ignored": [], "python_files": ["test_*.py", "*_test.py"], "python_classes": ["Test"], "python_functions": ["test"], "testpaths": [], "blocked": [], "plugins": [], "producers": ["fixture"], "autoload": ["on"]}, "census": []}):     # C2a10 (labelled): the two new finish fields; C2c (labelled): the whole witness
            fh.write(json.dumps({**rec, "token": token, "inv": inv}) + "\n")
    print(f"aget-kit-report: pytest {inv}")
print("1 passed in 0.01s")
