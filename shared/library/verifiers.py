"""Deterministic verifier registry for first-run checkpoints."""

import json
import re
import shlex
import subprocess
import hashlib
from pathlib import Path


def _result(verifier_type, passed, evidence, detail, target=None, expected=None, actual=None):
    return {
        "type": verifier_type,
        "passed": bool(passed),
        "evidence_id": f"{verifier_type}:{evidence or 'none'}",
        "evidence": evidence,
        "target": target or evidence,
        "expected": expected,
        "actual": actual if actual is not None else detail,
        "detail": detail,
    }


def command_exit(config, base_dir=None):
    command = config.get("command")
    if isinstance(command, str):
        command = shlex.split(command)
    if not command:
        return _result("command_exit", False, None, "missing command", expected="command")
    cwd = config.get("cwd") or base_dir
    completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    expected = int(config.get("expected_exit", 0))
    passed = completed.returncode == expected
    return _result(
        "command_exit",
        passed,
        f"exit:{completed.returncode}",
        (completed.stdout or completed.stderr or "").strip(),
        target=" ".join(command),
        expected=f"exit:{expected}",
        actual=f"exit:{completed.returncode}",
    )


def file_exists(config, base_dir=None):
    path = Path(config.get("path", ""))
    if base_dir and not path.is_absolute():
        path = Path(base_dir) / path
    passed = path.exists()
    return _result("file_exists", passed, str(path), "exists" if passed else "missing", target=str(path), expected="exists", actual="exists" if passed else "missing")


def _lookup(data, dotted_field):
    current = data
    for part in str(dotted_field or "").split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None, False
    return current, True


def json_field(config, base_dir=None):
    path = Path(config.get("path", ""))
    if base_dir and not path.is_absolute():
        path = Path(base_dir) / path
    if not path.exists():
        return _result("json_field", False, str(path), "missing json file", target=str(path), expected=config.get("field"), actual="missing")
    data = json.loads(path.read_text())
    value, found = _lookup(data, config.get("field"))
    if "equals" in config:
        passed = found and value == config["equals"]
    else:
        passed = found
    expected = config["equals"] if "equals" in config else "field present"
    return _result("json_field", passed, f"{path}:{config.get('field')}", repr(value), target=f"{path}:{config.get('field')}", expected=expected, actual=value if found else "missing")


def regex_text(config, base_dir=None):
    path = Path(config.get("path", ""))
    if base_dir and not path.is_absolute():
        path = Path(base_dir) / path
    if not path.exists():
        return _result("regex_text", False, str(path), "missing text file", target=str(path), expected=config.get("pattern"), actual="missing")
    text = path.read_text()
    pattern = config.get("pattern") or ""
    passed = bool(re.search(pattern, text, re.M))
    return _result("regex_text", passed, f"{path}:{pattern}", "matched" if passed else "no match", target=str(path), expected=pattern, actual="matched" if passed else "no match")


def file_diff(config, base_dir=None):
    before = Path(config.get("before", ""))
    after = Path(config.get("after", ""))
    if base_dir:
        if not before.is_absolute():
            before = Path(base_dir) / before
        if not after.is_absolute():
            after = Path(base_dir) / after
    if not before.exists() or not after.exists():
        return _result("file_diff", False, f"{before}->{after}", "missing file", target=f"{before}->{after}", expected="both files exist", actual="missing")
    same = before.read_text() == after.read_text()
    expect_changed = bool(config.get("expect_changed", True))
    passed = (not same) if expect_changed else same
    return _result("file_diff", passed, f"{before}->{after}", "changed" if not same else "same", target=f"{before}->{after}", expected="changed" if expect_changed else "same", actual="changed" if not same else "same")


def count_threshold(config, base_dir=None):
    path = Path(config.get("path", ""))
    if base_dir and not path.is_absolute():
        path = Path(base_dir) / path
    if not path.exists():
        return _result("count_threshold", False, str(path), "missing file", target=str(path), expected=config.get("minimum", 1), actual="missing")
    mode = config.get("mode", "lines")
    text = path.read_text()
    if mode == "regex":
        count = len(re.findall(config.get("pattern", ""), text, re.M))
    elif mode == "json_list":
        data = json.loads(text)
        field = config.get("field")
        value = _lookup(data, field)[0] if field else data
        count = len(value) if isinstance(value, list) else 0
    else:
        count = len([line for line in text.splitlines() if line.strip()])
    minimum = int(config.get("minimum", 1))
    maximum = config.get("maximum")
    passed = count >= minimum and (maximum is None or count <= int(maximum))
    expected = f">={minimum}" if maximum is None else f"{minimum}..{maximum}"
    return _result("count_threshold", passed, f"{path}:{mode}", str(count), target=str(path), expected=expected, actual=count)


def source_snapshot_hash(config, base_dir=None):
    path = Path(config.get("path", ""))
    if base_dir and not path.is_absolute():
        path = Path(base_dir) / path
    if not path.exists():
        return _result("source_snapshot_hash", False, str(path), "missing source", target=str(path), expected="sha256", actual="missing")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    expected = config.get("sha256")
    passed = bool(digest) if not expected else digest == expected
    return _result("source_snapshot_hash", passed, f"{path}:sha256", digest, target=str(path), expected=expected or "sha256 present", actual=digest)


REGISTRY = {
    "command_exit": command_exit,
    "file_exists": file_exists,
    "json_field": json_field,
    "regex_text": regex_text,
    "file_diff": file_diff,
    "count_threshold": count_threshold,
    "source_snapshot_hash": source_snapshot_hash,
}


def run_verifier(config, base_dir=None):
    verifier_type = config.get("type")
    if verifier_type not in REGISTRY:
        return _result(str(verifier_type), False, None, "unknown verifier type")
    return REGISTRY[verifier_type](config, base_dir=base_dir)


def run_verifiers(configs, base_dir=None):
    return [run_verifier(config, base_dir=base_dir) for config in configs]
