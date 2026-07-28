# Documentation Consolidation Certification v1

## Verdict: CERTIFIED

A new beta user can clone, install, doctor, run their first design, open the dashboard,
view telemetry, and generate a support bundle using only 3 documents.

## Documents Archived (198 files → docs/archive/)

| Origin | Count | Destination |
|--------|-------|-------------|
| docs/audit/ | 54 | docs/archive/audit/ |
| docs/reliability/ | 80 | docs/archive/reliability/ |
| docs/productization/ | 2 | docs/archive/productization/ |
| docs/intelligence/ | 10 | docs/archive/intelligence/ |
| docs/debug/ | 2 | docs/archive/debug/ |
| docs/architecture/ | 5 | docs/archive/architecture/ |
| docs/datasets/ | 4 | docs/archive/datasets/ |
| docs/compliance/ | 1 | docs/archive/compliance/ |
| docs/security/ | 1 | docs/archive/security/ |
| docs/developer/ | 11 | docs/archive/developer/ |
| docs/release/ | 3 | docs/archive/release/ |
| docs/failure_atlas/ | 1 | docs/archive/failure_atlas/ |
| docs/user-guide/ | 5 | docs/archive/user-guide/ |
| docs/user_guide/rtl-to-gdsii.md | 1 | docs/archive/ |
| **Total** | **180** | |

## Documents Deleted (8 files)

| File | Reason |
|------|--------|
| docs/guides/installation_guide.md | Content merged into user_manual.md |
| docs/guides/troubleshooting_guide.md | Content merged into troubleshooting.md |
| docs/guides/deployment_modes.md | Outdated, not user-facing |
| docs/setup/installation.md | Content merged into getting_started.md |
| docs/setup/quickstart.md | Content merged into getting_started.md |
| docs/telemetry/cloud_ingestion_architecture.md | Content merged into user_manual.md |
| docs/telemetry/consent_and_upload_architecture.md | Content merged into user_manual.md |
| docs/telemetry/important_run_architecture_audit.md | Developer doc, not user-facing |
| docs/user_guide/TERMS_OF_SERVICE.md | Duplicate of docs/legal/TERMS_OF_SERVICE.md |
| docs/user_guide/dashboard_guide.md | Content merged into dashboard.md |

## Documents Retained (10 user-facing)

| Document | Purpose |
|----------|---------|
| README.md | Single entry point |
| docs/user_guide/getting_started.md | 8-step onboarding |
| docs/user_guide/user_manual.md | Complete feature reference |
| docs/user_guide/dashboard.md | Dashboard pages guide |
| docs/user_guide/KNOWN_LIMITATIONS.md | Transparent limitations |
| docs/reference/cli_reference.md | CLI command reference |
| docs/reference/api_reference.md | API endpoint reference |
| docs/reference/troubleshooting.md | Issue resolution guide |
| docs/privacy/telemetry_and_privacy.md | Telemetry privacy policy |
| docs/legal/TERMS_OF_SERVICE.md | Terms of service |

Plus retained: CHANGELOG.md, CONTRIBUTING.md, SECURITY.md, LICENSE, example READMEs.

## Broken Links Fixed

**0 broken links** across all user-facing documents (35 internal links checked).

## Fresh User Walkthrough

| Command | Status |
|---------|--------|
| `git clone` | ✓ |
| `pip install -e .` | ✓ |
| `gli-flow doctor` | ✓ Environment READY |
| `gli-flow run examples/counter --mock` | ✓ QoR 0.60, Tapeout Ready |
| `gli-flow dashboard` | ✓ |
| `gli-flow telemetry status` | ✓ |
| `gli-flow support-bundle` | ✓ |
| `gli-flow history` | ✓ |
| `gli-flow diagnose` | ✓ |

**Documents used:** README.md → getting_started.md → user_manual.md (3 documents).

## Final Documentation Structure

```
README.md
CONTRIBUTING.md
SECURITY.md
CHANGELOG.md
docs/
  user_guide/
    getting_started.md
    user_manual.md
    dashboard.md
    KNOWN_LIMITATIONS.md
    USER_MANUAL.md          (redirect stub)
  reference/
    cli_reference.md
    api_reference.md
    troubleshooting.md
  privacy/
    telemetry_and_privacy.md
  legal/
    TERMS_OF_SERVICE.md
  archive/
    (198 historical reports — documentation team only)
```
