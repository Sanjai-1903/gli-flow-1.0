# Environment Validation

The `doctor` command validates your EDA toolchain and environment:

```bash
gli-flow doctor
```

Checks:
- Python version (3.9+)
- EDA tools: yosys, openroad, magic, netgen, klayout, sv2v
- PDK presence and configuration
- Environment variables (PDK_ROOT, ORFS_ROOT)
- Database health
- Docker availability (if applicable)

## Multi-Candidate Discovery

Doctor finds all copies of each tool on the system and selects the best one based on
functional validation. If a broken wrapper shadows a valid system binary (e.g., `magic`
version 0), doctor detects it:

```bash
gli-flow doctor --repair-magic   # Auto-repair magic PATH shadowing
```

## Auto-Repair

```bash
gli-flow doctor --fix            # Attempt to fix detected issues
```

See [CLI Reference](../reference/cli_reference.md) for all doctor flags.
