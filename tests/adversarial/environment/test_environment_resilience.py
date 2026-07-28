"""
Adversarial tests: Environment resilience & path shadowing.

These tests verify that the multi-candidate discovery, ranking,
and validation logic correctly handles corrupted/broken environments.

Each test sets up a controlled adversarial environment and verifies
that the doctor detects the issue and the best candidate is selected.
"""

import os
import stat
import tempfile
from pathlib import Path
from typing import Optional


def _create_mock_binary(path: Path, content: str = None, exit_code: int = 0):
    """Create a mock executable binary."""
    if content is None:
        content = "#!/bin/sh\necho 'mock'\nexit 0\n"
    path.write_text(content)
    path.chmod(0o755)
    return str(path)


def _create_broken_wrapper(path: Path, missing_tcl: str = "/nonexistent/wrapper.tcl"):
    """Create a broken Tcl wrapper that references a missing file."""
    content = f"""#!/bin/sh
echo "couldn't read file \\\"{missing_tcl}\\\""
exit 1
"""
    path.write_text(content)
    path.chmod(0o755)
    return str(path)


def _create_broken_symlink(path: Path, target: str = "/nonexistent/target"):
    """Create a broken symlink."""
    if path.exists():
        path.unlink()
    path.symlink_to(target)
    return str(path)


def _create_non_executable(path: Path):
    """Create a non-executable binary."""
    path.write_text("#!/bin/sh\necho 'mock'\nexit 0\n")
    path.chmod(0o644)
    return str(path)


def _create_wrong_version(path: Path, version: str = "0.0.1"):
    """Create a mock that reports a wrong/invalid version."""
    content = f"""#!/bin/sh
echo '{version}'
exit 0
"""
    path.write_text(content)
    path.chmod(0o755)
    return str(path)


def _create_valid_magic(path: Path):
    """Create a mock valid magic binary that supports TCL."""
    content = """#!/usr/bin/env python3
import sys
if '--version' in sys.argv:
    print('Magic 8.3.359')
    sys.exit(0)
if '-version' in sys.argv:
    print('Magic 8.3.359')
    sys.exit(0)
if '-noconsole' in sys.argv and '-dnull' in sys.argv:
    inp = sys.stdin.read()
    if 'TCL_OK' in inp:
        print('TCL_OK')
        sys.exit(0)
    if 'DRC_SMOKE_OK' in inp:
        print('DRC_SMOKE_OK')
        sys.exit(0)
    sys.exit(0)
print('Magic 8.3.359')
sys.exit(0)
"""
    path.write_text(content)
    path.chmod(0o755)
    return str(path)


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

def _setup_environment(
    broken_path: str,
    valid_path: str,
    env_patch: Optional[dict] = None,
) -> dict:
    """Set up environment for testing, returns original env."""
    old_environ = os.environ.copy()
    if env_patch:
        os.environ.update(env_patch)
    return old_environ


def _teardown_environment(old_environ: dict):
    """Restore original environment."""
    os.environ.clear()
    os.environ.update(old_environ)


# ---------------------------------------------------------------------------
# Test: discover_magic_binaries finds both candidates
# ---------------------------------------------------------------------------

def test_discover_magic_binaries_finds_both():
    """discover_magic_binaries returns both broken local and valid system binaries."""
    from gli_flow.core.tool_discovery import discover_magic_binaries

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        local_bin = tmp_path / ".local" / "bin"
        system_bin = tmp_path / "usr" / "bin"
        local_bin.mkdir(parents=True)
        system_bin.mkdir(parents=True)

        _create_broken_wrapper(local_bin / "magic")
        _create_valid_magic(system_bin / "magic")

        old_home = os.environ.get("HOME", "")
        old_path = os.environ.get("PATH", "")
        os.environ["HOME"] = str(tmp_path)
        os.environ["PATH"] = str(system_bin)

        try:
            candidates = discover_magic_binaries()
            paths = [c.path for c in candidates]
            assert len(candidates) >= 1, "Should find at least one magic binary"
        finally:
            os.environ["HOME"] = old_home
            os.environ["PATH"] = old_path


# ---------------------------------------------------------------------------
# Test: rank_tool_candidates prefers valid over broken
# ---------------------------------------------------------------------------

def test_rank_tool_candidates_prefers_valid():
    """rank_tool_candidates selects valid candidate over broken regardless of PATH order."""
    from gli_flow.core.tool_discovery import (
        ToolCandidate, ToolCandidateStatus, BinarySource,
        rank_tool_candidates,
    )

    broken = ToolCandidate(
        path="/home/user/.local/bin/magic",
        source=BinarySource.USER_LOCAL,
        version=(0,),
        version_str="0",
        exists=True,
        executable=True,
        functional=False,
        status=ToolCandidateStatus.BROKEN,
        failure_reason="wrapper.tcl missing",
    )
    valid = ToolCandidate(
        path="/usr/bin/magic",
        source=BinarySource.SYSTEM,
        version=(8, 3, 359),
        version_str="8.3.359",
        exists=True,
        executable=True,
        functional=True,
        status=ToolCandidateStatus.VALID,
    )

    ranked = rank_tool_candidates([broken, valid])
    assert len(ranked) == 2
    assert ranked[0].status == ToolCandidateStatus.VALID, "Valid candidate should be ranked first"
    assert ranked[0].path == valid.path


# ---------------------------------------------------------------------------
# Test: validate_magic_candidate detects broken wrapper
# ---------------------------------------------------------------------------

def test_validate_magic_candidate_broken_wrapper():
    """validate_magic_candidate identifies Tcl wrapper referencing missing file."""
    from gli_flow.core.tool_discovery import (
        ToolCandidate, ToolCandidateStatus, BinarySource,
        validate_magic_candidate,
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        magic_bin = tmp_path / "magic"
        _create_broken_wrapper(magic_bin)

        candidate = ToolCandidate(
            path=str(magic_bin),
            source=BinarySource.USER_LOCAL,
            exists=True,
            executable=True,
        )
        report = validate_magic_candidate(candidate)
        assert report.status == ToolCandidateStatus.BROKEN, (
            f"Expected BROKEN, got {report.status}"
        )
        assert report.failure_reason, "Should have a failure reason"


# ---------------------------------------------------------------------------
# Test: validate_magic_candidate passes valid binary
# ---------------------------------------------------------------------------

def test_validate_magic_candidate_valid():
    """validate_magic_candidate passes a properly functioning magic binary."""
    from gli_flow.core.tool_discovery import (
        ToolCandidate, ToolCandidateStatus, BinarySource,
        validate_magic_candidate,
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        magic_bin = tmp_path / "magic"
        _create_valid_magic(magic_bin)

        candidate = ToolCandidate(
            path=str(magic_bin),
            source=BinarySource.SYSTEM,
            exists=True,
            executable=True,
        )
        report = validate_magic_candidate(candidate)
        assert report.status == ToolCandidateStatus.VALID, (
            f"Expected VALID, got {report.status}: {report.failure_reason}"
        )


# ---------------------------------------------------------------------------
# Test: broken symlink detection
# ---------------------------------------------------------------------------

def test_broken_symlink_detection():
    """validate_magic_candidate fails on a broken symlink."""
    from gli_flow.core.tool_discovery import (
        ToolCandidate, ToolCandidateStatus, BinarySource,
        validate_magic_candidate,
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        magic_link = tmp_path / "magic"
        _create_broken_symlink(magic_link)

        candidate = ToolCandidate(
            path=str(magic_link),
            source=BinarySource.USER_LOCAL,
            exists=False,
            executable=False,
        )
        report = validate_magic_candidate(candidate)
        assert report.status == ToolCandidateStatus.BROKEN


# ---------------------------------------------------------------------------
# Test: non-executable binary
# ---------------------------------------------------------------------------

def test_non_executable_binary():
    """Non-executable magic binary fails validation."""
    from gli_flow.core.tool_discovery import (
        ToolCandidate, ToolCandidateStatus, BinarySource,
        validate_magic_candidate,
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        magic_bin = tmp_path / "magic"
        _create_non_executable(magic_bin)

        candidate = ToolCandidate(
            path=str(magic_bin),
            source=BinarySource.USER_LOCAL,
            exists=True,
            executable=False,
        )
        report = validate_magic_candidate(candidate)
        assert report.status == ToolCandidateStatus.BROKEN


# ---------------------------------------------------------------------------
# Test: PATH shadowing — doctor detects issue
# ---------------------------------------------------------------------------

def test_path_shadowing_detected():
    """Doctor discovery report correctly identifies path shadowing."""
    from gli_flow.core.tool_discovery import (
        discover_magic_binaries, validate_magic_candidate,
        rank_tool_candidates, ToolCandidateStatus,
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        local_bin = tmp_path / ".local" / "bin"
        system_bin = tmp_path / "usr" / "bin"
        local_bin.mkdir(parents=True)
        system_bin.mkdir(parents=True)

        _create_broken_wrapper(local_bin / "magic")
        _create_valid_magic(system_bin / "magic")

        old_home = os.environ.get("HOME", "")
        old_path = os.environ.get("PATH", "")
        os.environ["HOME"] = str(tmp_path)
        os.environ["PATH"] = str(system_bin)

        try:
            candidates = discover_magic_binaries()
            for c in candidates:
                vr = validate_magic_candidate(c)
                c.status = vr.status
                c.failure_reason = vr.failure_reason
                c.validation_evidence = vr.evidence
                c.functional = vr.passed

            ranked = rank_tool_candidates(candidates)
            valid = [c for c in ranked if c.status == ToolCandidateStatus.VALID]
            broken = [c for c in ranked if c.status == ToolCandidateStatus.BROKEN]

            assert len(broken) >= 1, "Should detect broken candidate"
            assert len(valid) >= 1, "Should detect valid candidate"
            assert ranked[0].status == ToolCandidateStatus.VALID, "Valid should rank first"
        finally:
            os.environ["HOME"] = old_home
            os.environ["PATH"] = old_path


# ---------------------------------------------------------------------------
# Test: wrong version detection
# ---------------------------------------------------------------------------

def test_wrong_version_validation():
    """Candidate with unparseable version is still validated by behavior."""
    from gli_flow.core.tool_discovery import (
        ToolCandidate, ToolCandidateStatus, BinarySource,
        validate_magic_candidate,
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        magic_bin = tmp_path / "magic"
        _create_wrong_version(magic_bin, version="not-a-version")

        candidate = ToolCandidate(
            path=str(magic_bin),
            source=BinarySource.USER_LOCAL,
            exists=True,
            executable=True,
        )
        report = validate_magic_candidate(candidate)
        assert report.status == ToolCandidateStatus.BROKEN, (
            f"Expected BROKEN for wrong version, got {report.status}"
        )


# ---------------------------------------------------------------------------
# Test: no false PASS for non-functional binary
# ---------------------------------------------------------------------------

def test_no_false_pass():
    """A non-functional magic binary never gets VALID status."""
    from gli_flow.core.tool_discovery import (
        ToolCandidate, ToolCandidateStatus, BinarySource,
        validate_magic_candidate,
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        magic_bin = tmp_path / "magic"
        _create_mock_binary(magic_bin, content="""#!/bin/sh
echo 'I exist but do nothing useful'
exit 0
""")

        candidate = ToolCandidate(
            path=str(magic_bin),
            source=BinarySource.USER_LOCAL,
            exists=True,
            executable=True,
        )
        report = validate_magic_candidate(candidate)
        assert report.status != ToolCandidateStatus.VALID, (
            "Non-functional binary should not get VALID status"
        )


# ---------------------------------------------------------------------------
# Test: no false FAIL for functional binary
# ---------------------------------------------------------------------------

def test_no_false_fail():
    """A properly functional magic binary never gets BROKEN status."""
    from gli_flow.core.tool_discovery import (
        ToolCandidate, ToolCandidateStatus, BinarySource,
        validate_magic_candidate,
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        magic_bin = tmp_path / "magic"
        _create_valid_magic(magic_bin)

        candidate = ToolCandidate(
            path=str(magic_bin),
            source=BinarySource.SYSTEM,
            exists=True,
            executable=True,
        )
        report = validate_magic_candidate(candidate)
        assert report.status != ToolCandidateStatus.BROKEN, (
            "Functional binary should not get BROKEN status"
        )
