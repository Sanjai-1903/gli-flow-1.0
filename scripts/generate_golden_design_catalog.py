import json
from gli_flow.synthetic.golden_designs import golden_design_catalog

# Assuming this script is run from the project root
output_path = "golden_design_catalog.json"

with open(output_path, "w") as f:
    json.dump(golden_design_catalog, f, indent=4)

print(f"Generated {output_path}")