# Synthetic Failure Factory & Dataset Generation Platform - v2

## 1. Executive Summary

This report details the implementation of the GLI Synthetic Failure Factory v2, a production-scale engine designed to generate large-scale, privacy-safe, and labeled execution intelligence datasets for semiconductor EDA research. The system is designed to achieve 100,000+ records, focusing on scale, coverage, quality, and automation.

## 2. Key Components

* **FailureCoverageMatrix (Phase 1):** Tracks coverage of failure types, root causes, tools, stages, PDKs, and designs to identify gaps.
* **Advanced Failure Injection (Phase 2):** Significantly expanded failure injection types, covering Timing (clock sweeps, skew, etc.), Congestion (density stress, etc.), Power (PDN starvation, etc.), Verification (LVS mismatches, etc.), and Tool Failures.
* **DatasetCampaignManager (Phase 3):** Orchestrates single, batch, and distributed campaigns with persistent metadata storage.
* **Mass Execution Engine (Phase 4):** Enables parallel execution with configurable workers (1-32+) and captures performance metrics (runtime, memory, success rate, yield).
* **DatasetEngine (Phases 5-9, 11):** A centralized engine handling:
    * **Resolution Validation:** Re-running failing designs with fixes and measuring outcomes (`ValidatedResolutionRecord`).
    * **QoR Evolution:** Capturing QoR trajectories over parameter changes (`QoREvolutionRecord`).
    * **Graph Feature Extraction:** Privacy-safe feature extraction (fanout, logic depth, etc.).
    * **Readiness Engine:** Calculates coverage scores (Failure, Root Cause, etc.) for a 0-100 `DatasetReadinessScore`.
    * **Quality Gates:** Enforces strict rejection criteria (missing telemetry, duplicates, etc.).
    * **Warehouse Storage:** Manages record storage, deduplication, and versioning.
* **CLI (`gli-flow dataset`) (Phase 10):** Provides a command-line interface for common operations (generate, campaign, coverage, quality, readiness, report).

## 3. Success Metrics

The pipeline can now automatically launch large-scale campaigns, generate thousands of validated records, continuously measure dataset quality, and ensure coverage, meeting the requirements of a high-quality execution intelligence dataset pipeline.

## 4. Privacy & Future Readiness

The system maintains strict privacy, avoiding storage of reconstructable IP (RTL, Netlists, DEF, LEF, GDS). All data generated is abstract, summarized, and metric-focused, preparing it for future high-quality EDA AI research.
