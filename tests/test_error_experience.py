"""Tests for the structured error experience system."""

import traceback

from gli_flow.core.error_experience import (
    ALL_ERROR_CODES,
    GliFlowError,
    LVS_FAILURE,
    MAGIC_DRC_MISSING,
    OOM_ERROR,
    PDK_NOT_FOUND,
    TIMEOUT_ERROR,
    TOOL_NOT_FOUND,
    format_debug_error,
    format_user_error,
    resolve_error,
)


class TestFormatUserError:
    """format_user_error must never expose raw stack traces."""

    def test_no_traceback_in_user_output(self):
        err = GliFlowError(
            error_code="E1001",
            message="test",
            cause="testing",
            debug_traceback="".join(traceback.format_stack()),
        )
        result = format_user_error(err)
        assert "Traceback" not in result
        assert "File \"" not in result
        assert ", line " not in result

    def test_user_output_contains_error_code(self):
        result = format_user_error(TOOL_NOT_FOUND)
        assert "E1001" in result

    def test_user_output_contains_message(self):
        result = format_user_error(LVS_FAILURE)
        assert "LVS" in result or "mismatch" in result

    def test_user_output_contains_resolution(self):
        result = format_user_error(OOM_ERROR)
        assert "Resolution" in result


class TestFormatDebugError:
    """format_debug_error must include tracebacks."""

    def test_includes_traceback_when_present(self):
        tb = "Traceback (most recent call last):\n  File \"test.py\", line 1, in <module>\n"
        err = GliFlowError(
            error_code="E1001",
            message="test",
            debug_traceback=tb,
        )
        result = format_debug_error(err)
        assert "Traceback" in result

    def test_omits_traceback_when_empty(self):
        err = GliFlowError(error_code="E1001", message="test")
        result = format_debug_error(err)
        assert "Traceback" not in result


class TestErrorCodesUnique:
    """All registered error codes must be unique."""

    def test_no_duplicate_codes(self):
        codes = list(ALL_ERROR_CODES)
        assert len(codes) == len(set(codes))


class TestResolveError:
    """resolve_error must return non-empty steps for all known codes."""

    def test_returns_steps_for_known_code(self):
        steps = resolve_error("E1001")
        assert len(steps) > 0
        assert "PATH" in steps or "tool" in steps

    def test_returns_fallback_for_unknown_code(self):
        steps = resolve_error("E9999")
        assert len(steps) > 0

    def test_all_registered_codes_have_steps(self):
        for code in ALL_ERROR_CODES:
            steps = resolve_error(code)
            assert len(steps) > 0, f"No resolution steps for {code}"


class TestPrebuiltTemplates:
    """Pre-built error templates must have correct error codes."""

    def test_tool_not_found_code(self):
        assert TOOL_NOT_FOUND.error_code == "E1001"

    def test_pdk_not_found_code(self):
        assert PDK_NOT_FOUND.error_code == "E1002"

    def test_drc_missing_code(self):
        assert MAGIC_DRC_MISSING.error_code == "E1003"

    def test_lvs_failure_code(self):
        assert LVS_FAILURE.error_code == "E1004"

    def test_oom_error_code(self):
        assert OOM_ERROR.error_code == "E1005"

    def test_timeout_error_code(self):
        assert TIMEOUT_ERROR.error_code == "E1006"

    def test_all_templates_have_non_empty_message(self):
        for err in [TOOL_NOT_FOUND, PDK_NOT_FOUND, MAGIC_DRC_MISSING,
                    LVS_FAILURE, OOM_ERROR, TIMEOUT_ERROR]:
            assert err.message, f"Empty message for {err.error_code}"
