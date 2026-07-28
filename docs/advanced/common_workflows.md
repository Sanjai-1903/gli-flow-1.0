# Common Workflows

## First-Time Setup
```bash
git clone https://github.com/Jegadiswar-SM/gli-flow-asic.git
cd gli-flow-asic
python3 -m venv venv
source venv/bin/activate
pip install -e .
gli-flow install
gli-flow doctor
gli-flow run examples/counter --mock
```

## Run a Custom Design
```bash
mkdir my_design
# Add RTL files and gli_manifest.yaml
gli-flow run my_design --mock      # Validate first
gli-flow run my_design              # Real run
```

## Investigate a Failure
```bash
gli-flow history                    # Find the run ID
gli-flow diagnose <run_id>          # Automated analysis
gli-flow dashboard                  # Visual investigation
```

## Reset Database
```bash
gli-flow reset-runs                 # Clear all run data
```
