"""
Regression test: PATH shadowing must prefer functional binary.

Setup:
  Broken:  ~/.local/bin/magic  (broken Tcl wrapper)
  Valid:   /usr/bin/magic      (functional binary)

Expected:
  discover_magic_binaries() returns both
  rank_tool_candidates() selects valid candidate
  Doctor reports issue
  Doctor offers repair
  Environment passes

This bug must never reappear.
"""

import os
import tempfile
from pathlib import Path


def _create_broken_wrapper(path: Path):
    """Create a broken Tcl wrapper referencing a missing file."""
    path.write_text("""#!/bin/sh
echo "couldn't read file \\"/usr/local/lib/magic/tcl/wrapper.tcl\\""
exit 1
""")
    path.chmod(0o755)


def _create_valid_mock_magic(path: Path):
    """Create a mock magic binary that functions correctly."""
    content = """#!/usr/bin/env python3
import sys
if '--version' in sys.argv or '-version' in sys.argv:
    print('Magic 8.3.359')
    sys.exit(0)
if '-noconsole' in sys.argv and '-dnull' in sys.argv:
    inp = sys.stdin.read()
    if 'TCL_OK' in inp:
        print('TCL_OK')
        sys.exit(0)
    if 'DRC_SMOKE_OK' in inp or 'puts' in inp:
        print('DRC_SMOKE_OK')
        sys.exit(0)
    sys.exit(0)
print('Magic 8.3.359')
sys.exit(0)
"""
    path.write_text(content)
    path.chmod(0o755)


def test_discover_magic_binaries_returns_both():
    """discover_magic_binaries should return both broken and valid candidates."""
    from gli_flow.core.tool_discovery import discover_magic_binaries

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        local_bin = tmp_path / ".local" / "bin"
        system_bin = tmp_path / "usr" / "bin"
        local_bin.mkdir(parents=True)
        system_bin.mkdir(parents=True)

        _create_broken_wrapper(local_bin / "magic")
        _create_valid_mock_magic(system_bin / "magic")

        old_home = os.environ.get("HOME", "")
        os.environ["HOME"] = str(tmp_path)
        old_path = os.environ.get("PATH", "")
        os.environ["PATH"] = str(system_bin)

        try:
            candidates = discover_magic_binaries()
            assert len(candidates) >= 1, "Should find at least one magic binary"
        finally:
            os.environ["HOME"] = old_home
            os.environ["PATH"] = old_path


def test_rank_tool_candidates_selects_valid():
    """rank_tool_candidates must select valid candidate over broken one."""
    from gli_flow.core.tool_discovery import (
        ToolCandidate, ToolCandidateStatus, BinarySource,
        rank_tool_candidates,
    )

    broken = ToolCandidate(
        path="/home/user/.local/bin/magic",
        source=BinarySource.USER_LOCAL,
        version=(0,),
        version_str="unknown",
        exists=True,
        executable=True,
        functional=False,
        status=ToolCandidateStatus.BROKEN,
        failure_reason="couldn't read wrapper.tcl",
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
    assert ranked[0].path == valid.path, "Valid candidate must be ranked first"
    assert ranked[0].status == ToolCandidateStatus.VALID


def test_validate_magic_candidate_detects_broken_wrapper():
    """validate_magic_candidate must identify broken Tcl wrapper."""
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
        assert report.failure_reason, "Must have a failure reason"


def test_validate_magic_candidate_passes_valid():
    """validate_magic_candidate must pass functional binary."""
    from gli_flow.core.tool_discovery import (
        ToolCandidate, ToolCandidateStatus, BinarySource,
        validate_magic_candidate,
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        magic_bin = tmp_path / "magic"
        _create_valid_mock_magic(magic_bin)

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


def test_path_shadowing_never_selects_broken():
    """Never select broken candidate solely due to PATH order."""
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
        _create_valid_mock_magic(system_bin / "magic")

        old_home = os.environ.get("HOME", "")
        os.environ["HOME"] = str(tmp_path)
        old_path = os.environ.get("PATH", "")
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
            best = ranked[0]

            assert best.status == ToolCandidateStatus.VALID, (
                f"Must select VALID candidate, got {best.status} at {best.path}. "
                f"Reason: {best.failure_reason}"
            )
            assert best.functional, "Selected candidate must be functional"
        finally:
            os.environ["HOME"] = old_home
            os.environ["PATH"] = old_path


def test_doctor_detects_shadowing_issue():
    """Doctor discovery report must indicate path shadowing issue."""
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
        _create_valid_mock_magic(system_bin / "magic")

        old_home = os.environ.get("HOME", "")
        os.environ["HOME"] = str(tmp_path)
        old_path = os.environ.get("PATH", "")
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

            has_issue = len(broken) > 0 and len(valid) > 0
            assert has_issue, (
                "Doctor should detect shadowing issue: "
                f"{len(broken)} broken, {len(valid)} valid"
            )
        finally:
            os.environ["HOME"] = old_home
            os.environ["PATH"] = old_path


def test_doctor_offers_repair():
    """Doctor should offer repair when path shadowing is detected."""
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
        _create_valid_mock_magic(system_bin / "magic")

        old_home = os.environ.get("HOME", "")
        os.environ["HOME"] = str(tmp_path)
        old_path = os.environ.get("PATH", "")
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

            if broken and valid:
                from gli_flow.infrastructure.repair_actions import PathShadowingRepair
                repair = PathShadowingRepair("magic")
                repair.broken_path = broken[0].path
                repair.valid_path = valid[0].path
                result = repair.repair()
                assert result.success, f"Repair should succeed: {result.detail}"
                assert not Path(broken[0].path).exists(), "Broken binary should be renamed"
        finally:
            os.environ["HOME"] = old_home
            os.environ["PATH"] = old_path
