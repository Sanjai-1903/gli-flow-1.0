# Reproducibility

GLI-FLOW captures per-run reproducibility metadata to enable deterministic replay and audit.

## What is captured

Each run generates `outputs/runs/<run_id>/reproducibility.json` containing:
- SHA256 hashes of all RTL files and configuration
- Tool versions (yosys, openroad, magic, netgen, klayout)
- System fingerprint (OS, kernel, CPU)
- Environment variables (redacted for secrets)
- Git commit hash of GLI-FLOW

## Verification

```bash
# Compare two runs for reproducibility
gli-flow history --compare <run_id_1> <run_id_2>

# Check environment fingerprint
cat outputs/runs/<run_id>/reproducibility.json
```
