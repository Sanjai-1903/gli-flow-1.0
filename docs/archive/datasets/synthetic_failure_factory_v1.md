# Synthetic Failure Factory & Dataset Generation Platform - v1

## 1. Introduction

This document outlines the architecture and implementation of the GLI Synthetic Failure Factory & Dataset Generation Platform. The platform's mission is to generate large-scale, privacy-safe, reproducible, and labeled ASIC and FPGA execution intelligence datasets without requiring external user data. These datasets are crucial for advancing research in Failure Atlas growth, Resolution Intelligence, Trust Scoring validation, GLI-SDI, QoR prediction, flow optimization, and future AI/EDA systems.

## 2. Platform Architecture

The platform is designed in several phases, each contributing a critical component to the overall data generation pipeline.

### Phase 1: Golden Design Library (Implemented in `gli_flow/synthetic/golden_designs.py`)

**Purpose:** To establish a foundational library of golden reference designs.

**Key Components:**
- **`GoldenDesign` dataclass:** Stores metadata for each design, including:
    - `name`, `top_module`, `pdk`, `clock_period_ns`, `design_type`
    - `expected_qor`, `expected_wns`, `expected_tns`, `expected_utilization`, `expected_cell_count`
    - `base_metrics` (synthetic baseline for injection), `manifest_path`, `tags`
    - `fingerprint` (derived for unique identification).
- **`SyntheticDatasetManager` class:** Provides methods to list, retrieve, and filter golden designs.
- **`GOLDEN_DESIGNS` list:** A pre-populated list of reference designs including `counter`, `gcd`, `uart`, `gpio`, `fir`, `picorv32`, and `ibex`.
- **`golden_design_catalog.json`:** A generated JSON file containing a catalog of all golden designs and their key attributes, serving as a public interface for the design library.

### Phase 2: Failure Injection Framework (Implemented in `gli_flow/synthetic/failure_injector.py`)

**Purpose:** To systematically introduce various types of failures into the design flow.

**Key Components:**
- **`InjectionType` Enum:** Defines a comprehensive list of supported failure injection categories:
    - `CLOCK_PERIOD_SWEEP`, `UTILIZATION_SWEEP`, `FLOORPLAN_SHRINK`, `MACRO_CONGESTION`
    - `PDN_STRESS`, `ROUTING_CONGESTION`, `TIMING_CONSTRAINT_ERRORS`, `MISSING_CONSTRAINTS`
    - `DRC_VIOLATIONS`, `LVS_MISMATCHES`, `TOOL_CONFIGURATION_ERRORS`
- **`InjectionConfig` dataclass:** Configures a single failure injection, including its type, parameters, description, and a `seed` for reproducibility.
- **`FailureInjector` class:** Contains the logic to apply a specified injection to a given design. It includes placeholder methods for each injection type, which in a full implementation would modify design files or tool configurations.

**Reproducibility:** Every injection is designed to be reproducible through the use of a `seed` in the `InjectionConfig`.

### Phase 3: Execution Campaign Engine (Implemented in `gli_flow/synthetic/campaign_runner.py`)

**Purpose:** To automate the execution of synthetic design runs, including parameter variations and failure injections, and capture their outcomes.

**Key Components:**
- **`SyntheticRunResult` dataclass:** Captures the outcome of a single synthetic execution, including:
    - `design_name`, `injection_config`, `runtime_sec`, `status`, `root_cause`, `telemetry_summary`
    - `resolution_candidate`, `run_seed`, `qor`, `fingerprint`.
- **`CampaignResult` dataclass:** Aggregates results from an entire campaign, providing summaries like `campaign_id`, `total_runs`, `successful_runs`, `failed_runs`, and a list of `SyntheticRunResult` instances.
- **`CampaignRunner` class:** Orchestrates campaigns by:
    - Running multiple variations for a given `GoldenDesign`.
    - Randomly applying specified `InjectionType`s via the `FailureInjector`.
    - Simulating design execution (with placeholder logic for various outcomes).
    - Ensuring run-level reproducibility using seeds.

### Phase 4: Dataset Record Schema (Implemented in `gli_flow/synthetic/dataset_records.py`)

**Purpose:** To define standardized schemas for different types of training records.

**Key Components:**
- **`FailureTrainingRecord` dataclass:** Stores details of a failed execution, including:
    - `failure_fingerprint` (derived), `failure_type`, `tool`, `stage`, `telemetry_summary`
    - `root_cause`, `resolution`, `trust_score`.
    - Includes a static method `calculate_fingerprint` for consistent identification.
- **`ResolutionTrainingRecord` dataclass:** Links failures to applied fixes and their outcomes.
- **`QoRTrainingRecord` dataclass:** Records changes in Quality of Results (QoR) due to parameter variations.
- **`GraphTrainingRecord` dataclass:** Stores privacy-safe graph features of designs.
- **`TrainingDataset` dataclass:** A container to hold collections of all types of training records.

**Privacy Guarantees:** The schemas explicitly avoid storing sensitive design information such as RTL, Netlists, DEF, LEF, or GDS data. Instead, they focus on high-level summaries, metrics, and abstract representations.

### Phase 5: Resolution Dataset Generation (Schema Defined in `gli_flow/synthetic/dataset_records.py`)

**Purpose:** To generate datasets for training resolution intelligence models.

**Status:** The schema for `ResolutionTrainingRecord` is defined. The actual generation of these records is integrated into the `CampaignRunner`'s output processing, where simulated `resolution_candidate` from `SyntheticRunResult` instances are converted into `ResolutionTrainingRecord`s.

### Phase 6: QoR Evolution Dataset (Schema Defined in `gli_flow/synthetic/dataset_records.py`)

**Purpose:** To capture how QoR changes in response to parameter variations.

**Status:** The schema for `QoRTrainingRecord` is defined. Data for this will be generated by observing parameter changes and their impact on simulated QoR metrics during campaign execution, with processing into records handled downstream.

### Phase 7: Graph Dataset Preparation (Schema Defined in `gli_flow/synthetic/dataset_records.py`)

**Purpose:** To prepare privacy-safe graph features of designs for training.

**Status:** The schema for `GraphTrainingRecord` is defined. The extraction of specific graph features (e.g., fanout distributions, logic depth, resource histograms) will require specialized parsing logic, ensuring no reconstructable IP is stored.

### Phase 8: Dataset Quality Engine (Implemented in `gli_flow/synthetic/quality_engine.py`)

**Purpose:** To ensure the quality, consistency, and validity of the generated datasets.

**Key Components:**
- **`QualityReport` dataclass:** Summarizes the findings of various quality checks.
- **`QualityEngine` class:** Provides methods for:
    - **Deduplication:** Prevents duplicate failure records.
    - **Label Validation:** Checks the integrity and correctness of labels (e.g., root cause, resolution).
    - **Consistency Checks:** Ensures logical consistency across related fields.
    - **Outlier Detection:** Identifies anomalous data points in metrics.

**Data Quality Controls:** The `QualityEngine` is central to maintaining data quality by actively identifying and, in some cases, mitigating issues like duplicate failures, corrupt labels, and invalid telemetry.

### Phase 9: Dataset Dashboard (Demonstrated by `gli_flow/synthetic/dashboard_reporter.py`)

**Purpose:** To provide visibility into the generated datasets and the platform's progress.

**Key Components:**
- **`DashboardReporter` class:** An API-like component that calculates and presents aggregate metrics, such as:
    - `Generated Runs`, `Unique Failures`, `Unique Resolutions`
    - `Atlas Coverage Growth` (placeholder for future implementation)
    - `Trust Distribution`, `Dataset Size`.
- **`generate_sample_dashboard_data` function:** Demonstrates the end-to-end flow from design selection, through campaign execution and quality checks, to the final reporting of dashboard metrics. This serves as a backend interface for a potential frontend dashboard.

## 3. Future AI Readiness

The platform's design explicitly supports future AI/ML research by generating structured, labeled datasets for various critical aspects of ASIC/FPGA design flow. The defined schemas for `FailureTrainingRecord`, `ResolutionTrainingRecord`, `QoRTrainingRecord`, and `GraphTrainingRecord` are tailored for supervised learning tasks. The `trust_score` in `FailureTrainingRecord` allows for weighted learning or filtering based on label confidence. The emphasis on reproducibility and data quality ensures that the generated datasets are reliable for training robust AI models.

## 4. Conclusion

The GLI Synthetic Failure Factory & Dataset Generation Platform provides a robust and extensible framework for creating high-quality, privacy-safe execution intelligence datasets. By systematically generating golden designs, injecting failures, running campaigns, and applying stringent quality controls, the platform lays the groundwork for advanced AI-driven EDA solutions. A single command can effectively generate thousands of labeled, privacy-safe execution intelligence records, fulfilling the primary success criteria.
