# Troubleshooting

## CLI Not Found

**Symptom:** `gli-flow: command not found`

```bash
# Activate virtual environment
source venv/bin/activate

# Or add pip's bin directory to PATH
export PATH="$HOME/.local/bin:$PATH"
```

To make the PATH change permanent, add it to `~/.bashrc`.

## PDK Missing or Not Found

**Symptom:** Doctor reports PDK errors or flows fail with PDK-related messages.

```bash
# Set PDK_ROOT environment variable
export PDK_ROOT=/path/to/your/pdk

# Make permanent
echo 'export PDK_ROOT=/path/to/your/pdk' >> ~/.bashrc
```

If the PDK is not installed:
```bash
gli-flow install
```

## Magic Version 0 or Unknown

**Symptom:** `gli-flow doctor` shows `magic version 0` or `magic version unknown`.

A broken wrapper script in `~/.local/bin/magic` shadows the valid system binary. The wrapper references a missing file.

```bash
# Auto-repair
gli-flow doctor --repair-magic

# Manual repair
mv ~/.local/bin/magic ~/.local/bin/magic.broken

# Verify
gli-flow doctor
```

## Dashboard Not Starting

**Symptom:** `gli-flow dashboard` fails or the page doesn't load.

```bash
# Check if port is already in use
lsof -i :5173
lsof -i :8000

# Kill existing processes
kill <PID>

# Try backend-only mode
gli-flow dashboard --backend-only
# Then open http://127.0.0.1:8000/docs in browser
```

## Telemetry Upload Failure

**Symptom:** Telemetry upload fails (visible in dashboard Telemetry Health page).

```bash
# Check connectivity
curl -I https://api.gli-flow.dev

# View telemetry status
gli-flow telemetry status

# Preview what would be uploaded
gli-flow telemetry preview

# If upload fails repeatedly, switch to local mode
gli-flow telemetry mode local
```

## Permission Issues

**Symptom:** Permission denied errors when accessing PDK or run directories.

```bash
# Fix PDK file permissions
chmod -R +r $PDK_ROOT

# Fix run directory ownership
chown -R $USER:$USER outputs/runs/
```

## Database Issues

**Symptom:** Database locked or corrupted.

```bash
# Remove stale lock file
rm -f ~/.gli-flow/gli_flow.db-journal

# Check database integrity
python3 -c "import sqlite3; conn=sqlite3.connect('~/.gli-flow/gli_flow.db'); print(conn.execute('PRAGMA integrity_check').fetchall())"

# Reset all run data
gli-flow reset-runs
```

## Out of Memory

**Symptom:** Flow crashes with `Killed` or `MemoryError`.

```bash
# Reduce parallel threads
gli-flow run <design> --threads 2

# Increase swap
sudo fallocate -l 8G /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Use Docker image (may have higher limits)
docker run -it --rm gli-flow:local
```

## Support Bundle

When reporting an issue, generate a diagnostic archive:

```bash
gli-flow support-bundle
```

Attach the generated `support-bundle.zip` to your GitHub issue. The archive contains version info, run summaries, system info, and configuration — no design data.

## Getting Help

- **GitHub Issues:** https://github.com/Jegadiswar-SM/gli-flow-asic/issues
- **Diagnose a run:** `gli-flow diagnose <run_id>`
- **AI investigation:** `gli-flow investigate <run_id>` (requires AI provider configuration)
