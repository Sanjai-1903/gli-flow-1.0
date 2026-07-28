"""
RTL preprocessing: SystemVerilog detection and sv2v conversion before synthesis.
"""

import subprocess
import shutil
import logging
import re
from pathlib import Path
from typing import List, Tuple

log = logging.getLogger(__name__)

SV_EXTENSIONS = {'.sv', '.svh', '.svi'}
V_EXTENSIONS = {'.v', '.vh'}


def detect_systemverilog(rtl_files: List[str]) -> List[str]:
    """Return list of files that are SystemVerilog."""
    sv_files = []
    for f in rtl_files:
        if Path(f).suffix.lower() in SV_EXTENSIONS:
            sv_files.append(f)
        else:
            try:
                content = Path(f).read_text(errors='ignore')
                sv_indicators = [
                    'always_ff', 'always_comb', 'always_latch', 'logic ',
                    'interface ', 'package ', 'typedef ', 'enum ',
                    'struct ', 'modport', 'import ', '::',
                ]
                if any(kw in content for kw in sv_indicators):
                    sv_files.append(f)
                    log.warning(f"File {f} has .v extension but contains SystemVerilog constructs.")
            except Exception as e:
                log.warning(f"Could not read {f} for SV detection: {e}")
    return sv_files


def convert_sv_to_v(
    sv_files: List[str],
    output_dir: Path,
    include_paths: List[str] = None
) -> Tuple[List[str], bool]:
    """Convert SystemVerilog files to Verilog-2005 using sv2v."""
    from gli_flow.core.tool_discovery import find_sv2v_binary
    sv2v_tb = find_sv2v_binary()
    sv2v_path = sv2v_tb.path if sv2v_tb else None
    if not sv2v_path:
        raise RuntimeError(
            "sv2v not found. SystemVerilog files cannot be synthesized without sv2v.\n"
            "Install: https://github.com/zachjs/sv2v/releases\n"
            "Or: gli-flow install --sv2v"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    converted = []

    inc_flags = []
    if include_paths:
        for p in include_paths:
            inc_flags.extend(['-I', p])

    cmd = [sv2v_path] + inc_flags + sv_files
    output_file = output_dir / "converted_sv.v"

    from gli_flow.core.subprocess_env import safe_env
    result = subprocess.run(cmd, capture_output=True, text=True, env=safe_env(), timeout=300)

    if result.returncode != 0:
        raise RuntimeError(f"sv2v conversion failed:\n{result.stderr}")

    if not result.stdout.strip():
        raise RuntimeError("sv2v produced empty output. Check SystemVerilog file syntax.")

    if "module" not in result.stdout:
        raise RuntimeError("sv2v output does not contain any Verilog modules. Conversion may have failed silently.")

    output_file.write_text(result.stdout)
    log.info(f"sv2v: converted {len(sv_files)} SystemVerilog files to {output_file}")

    converted.append(str(output_file))
    return converted, True


def preprocess_rtl(
    rtl_files: List[str],
    run_dir: Path,
    include_paths: List[str] = None
) -> List[str]:
    """Preprocess RTL files. Converts SV to V if needed."""
    sv_files = detect_systemverilog(rtl_files)
    v_files = [f for f in rtl_files if f not in sv_files]

    if sv_files:
        log.info(f"SystemVerilog detected in {len(sv_files)} file(s). Preprocessing with sv2v...")
        sv_output_dir = run_dir / "sv2v_output"
        converted, ok = convert_sv_to_v(sv_files, sv_output_dir, include_paths)
        return v_files + converted

    return rtl_files


def extract_include_paths(rtl_files: List[str]) -> List[str]:
    """Extract all `include paths from RTL files."""
    include_dirs = set()

    for rtl_file in rtl_files:
        try:
            content = Path(rtl_file).read_text(errors='ignore')
            includes = re.findall(r'`include\s+"([^"]+)"', content)
            for inc in includes:
                inc_path = Path(inc)
                if inc_path.is_absolute():
                    include_dirs.add(str(inc_path.parent))
                else:
                    src_dir = Path(rtl_file).parent
                    include_dirs.add(str(src_dir))
        except Exception as e:
            log.warning(f"Could not read {rtl_file} for include extraction: {e}")

    for rtl_file in rtl_files:
        include_dirs.add(str(Path(rtl_file).parent))

    return list(include_dirs)
