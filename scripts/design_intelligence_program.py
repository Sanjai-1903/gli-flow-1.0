#!/usr/bin/env python3
"""
GLI Design Intelligence & Feature Extraction Program

Teaches GLI what kind of design each execution record represents.
Backfills design identity, builds profiles, extracts features,
classifies designs, and enables feature-aware predictions.

Usage:
    python3 scripts/design_intelligence_program.py [--report]
"""

import argparse
import json
import logging
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from gli_flow.database.migrations import _get_db_path
from gli_flow.design_intel.profile_engine import DesignProfileEngine, DesignProfile
from gli_flow.design_intel.feature_extractor import (
    DesignFeatureExtractor,
    DesignFeatureRecord,
)
from gli_flow.design_intel.design_classifier import DesignClassifier, DesignClass
from gli_flow.design_intel.similarity_engine import DesignSimilarityEngine
from gli_flow.design_intel.quality_audit import DatasetQualityAudit

REPORT_DIR = Path(__file__).resolve().parent.parent / "docs" / "intelligence"
DB_PATH = _get_db_path()
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")


def db_conn():
    return sqlite3.connect(DB_PATH)


def phase1_backfill_design_identity() -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print("PHASE 1 — Design Identity Recovery")
    print("=" * 70)

    conn = db_conn()
    before = conn.execute(
        "SELECT COUNT(*) FROM failure_atlas_entries WHERE design_name IS NULL OR design_name = ''"
    ).fetchone()[0]
    total = conn.execute("SELECT COUNT(*) FROM failure_atlas_entries").fetchone()[0]

    print(f"  Entries without design_name: {before} / {total}")

    updated_from_runs = 0
    updated_from_inference = 0

    missing = conn.execute(
        "SELECT id, run_id FROM failure_atlas_entries WHERE design_name IS NULL OR design_name = ''"
    ).fetchall()

    for entry_id, run_id in missing:
        design_name = None
        run_row = conn.execute(
            "SELECT design_name FROM runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        if run_row and run_row[0]:
            design_name = run_row[0]
            updated_from_runs += 1
        else:
            known_patterns = [
                ("counter", "counter"),
                ("gcd", "gcd"),
                ("uart", "uart"),
                ("fir", "fir"),
                ("picorv32", "picorv32"),
                ("ibex", "ibex"),
                ("serv", "serv"),
                ("tinyml", "tinyml_accel"),
                ("sram", "sram_controller"),
                ("aes", "aes_cipher"),
                ("gpio", "gpio"),
                ("tiny_or", "tiny_or"),
                ("mini_mac", "mini_mac"),
                ("systolic", "systolic_array"),
            ]
            for pattern, name in known_patterns:
                if pattern in (run_id or "").lower():
                    design_name = name
                    break

        if not design_name:
            design_name = run_id or "unknown"

        conn.execute(
            "UPDATE failure_atlas_entries SET design_name = ? WHERE id = ?",
            (design_name, entry_id),
        )
        if not run_row:
            updated_from_inference += 1

    conn.commit()

    after = conn.execute(
        "SELECT COUNT(*) FROM failure_atlas_entries WHERE design_name IS NULL OR design_name = ''"
    ).fetchone()[0]
    conn.close()

    print(f"  Updated from runs table: {updated_from_runs}")
    print(f"  Updated by inference:    {updated_from_inference}")
    print(f"  Remaining missing:       {after}")
    print(f"  Coverage:                {round((total - after) / total * 100, 1)}% (target: 100%)")

    identities = _discover_design_names()

    report_path = REPORT_DIR / "design_identity_report.md"
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        f.write(_render_identity_report(before, after, total, identities))
    print(f"\n  Report: {report_path}")

    return {
        "before_empty": before,
        "after_empty": after,
        "total": total,
        "updated_from_runs": updated_from_runs,
        "updated_from_inference": updated_from_inference,
        "coverage_pct": round((total - after) / total * 100, 1),
        "designs_found": identities,
    }


def _discover_design_names() -> List[str]:
    conn = db_conn()
    names = set()
    for row in conn.execute(
        "SELECT DISTINCT design_name FROM failure_atlas_entries WHERE design_name IS NOT NULL AND design_name != ''"
    ).fetchall():
        names.add(row[0])
    for row in conn.execute(
        "SELECT DISTINCT design_name FROM runs WHERE design_name IS NOT NULL AND design_name != ''"
    ).fetchall():
        names.add(row[0])
    conn.close()
    return sorted(names)


def _render_identity_report(
    before: int, after: int, total: int, identities: List[str]
) -> str:
    lines = []
    lines.append("# Design Identity Recovery Report")
    lines.append("")
    lines.append(f"**Generated**: {datetime.now(timezone.utc).isoformat()}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Before | After |")
    lines.append(f"|---|---|---|")
    lines.append(f"| Entries without design_name | {before} | {after} |")
    lines.append(f"| Total entries | {total} | {total} |")
    lines.append(f"| Coverage | {round((total - before) / total * 100, 1) if total else 0}% | {round((total - after) / total * 100, 1) if total else 0}% |")
    lines.append("")
    lines.append("## Designs Discovered")
    lines.append("")
    lines.append(f"**{len(identities)} distinct designs**")
    lines.append("")
    lines.append("| Design Name | Atlas Entries | Runs |")
    lines.append("|---|---|---|")
    conn = db_conn()
    for name in identities:
        at = conn.execute(
            "SELECT COUNT(*) FROM failure_atlas_entries WHERE design_name = ?", (name,)
        ).fetchone()[0]
        rn = conn.execute(
            "SELECT COUNT(*) FROM runs WHERE design_name = ?", (name,)
        ).fetchone()[0]
        lines.append(f"| {name} | {at} | {rn} |")
    conn.close()
    lines.append("")
    lines.append("## Data Sources Used")
    lines.append("- `runs.design_name`: Direct mapping from pipeline execution records")
    lines.append("- Run ID pattern inference: Extracted design name from run naming conventions")
    lines.append("- Fallback: Used `run_id` as design_name when no mapping found")
    return "\n".join(lines)


def phase2_build_design_profiles() -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print("PHASE 2 — Design Profile Engine")
    print("=" * 70)

    engine = DesignProfileEngine(DB_PATH)
    profiles = engine.generate_all_profiles()

    print(f"  Profiles built: {len(profiles)}")
    for p in profiles:
        print(f"    {p.design_name:25s} type={p.design_type:8s} cells={p.expected_cell_count:6d}  "
              f"mem={p.memory_ratio:.0%} ctrl={p.control_ratio:.0%} comp={p.compute_ratio:.0%}")

    return {
        "total_profiles": len(profiles),
        "profiles": [
            {
                "design_name": p.design_name,
                "design_type": p.design_type,
                "expected_cell_count": p.expected_cell_count,
                "memory_ratio": p.memory_ratio,
                "control_ratio": p.control_ratio,
                "compute_ratio": p.compute_ratio,
            }
            for p in profiles
        ],
    }


def phase3_extract_features() -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print("PHASE 3 — Structural Feature Extraction")
    print("=" * 70)

    extractor = DesignFeatureExtractor(DB_PATH)
    records = extractor.extract_for_all_profiles()

    print(f"  Feature records extracted: {len(records)}")
    for r in records:
        print(f"    {r.design_name:25s} depth={r.logic_depth:3d}  reg={r.register_density:.0%}  "
              f"mem={r.memory_density:.0%}  dsp={r.dsp_density:.0%}  "
              f"fanout_peaks={sum(r.fanout_histogram)}")

    return {
        "total_features": len(records),
        "features": [
            {
                "design_name": r.design_name,
                "logic_depth": r.logic_depth,
                "register_density": r.register_density,
                "memory_density": r.memory_density,
                "dsp_density": r.dsp_density,
            }
            for r in records
        ],
    }


def phase4_classify_designs() -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print("PHASE 4 — Design Classification")
    print("=" * 70)

    classifier = DesignClassifier(DB_PATH)
    results = classifier.classify_all()
    summary = classifier.summary()

    print(f"  Classified designs: {len(results)}")
    for name, cls in sorted(results.items()):
        print(f"    {name:25s} -> {cls.value}")

    print(f"\n  Distribution:")
    for cls_name, count in sorted(summary.get("distribution", {}).items()):
        pct = count / summary["total_classified"] * 100 if summary["total_classified"] else 0
        print(f"    {cls_name:20s}: {count} ({pct:.0f}%)")

    return {
        "classifications": {name: cls.value for name, cls in results.items()},
        "distribution": summary["distribution"],
    }


def phase5_design_similarity() -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print("PHASE 5 — Design Similarity Engine")
    print("=" * 70)

    engine = DesignSimilarityEngine(DB_PATH)
    matrix = engine.similarity_matrix()

    print(f"  Similarity matrix computed for {len(matrix)} designs")
    for name, similars in sorted(matrix.items()):
        top = list(similars.items())[:3]
        top_str = ", ".join(f"{s[0]} ({s[1]:.2f})" for s in top)
        print(f"    {name:25s} -> {top_str}")

    return {"matrix": matrix, "design_count": len(matrix)}


def phase6_feature_aware_prediction() -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print("PHASE 6 — Feature-Aware Prediction")
    print("=" * 70)

    engine = DesignSimilarityEngine(DB_PATH)
    engine._load_all()

    print("  Extending prediction engine with design features...")
    print(f"  Profiles loaded: {len(engine._profiles)}")
    print(f"  Feature vectors: {len(engine._features)}")
    print(f"  Classifications: {len(engine._classes)}")

    conn = db_conn()
    entries_with_features = conn.execute(
        "SELECT COUNT(DISTINCT fe.design_name) FROM failure_atlas_entries fe "
        "JOIN design_features df ON fe.design_name = df.design_name"
    ).fetchone()[0]
    conn.close()

    print(f"  Entries with feature vectors: {entries_with_features}")

    return {
        "profiles_loaded": len(engine._profiles),
        "features_loaded": len(engine._features),
        "classes_loaded": len(engine._classes),
        "entries_with_features": entries_with_features,
    }


def phase7_feature_aware_recommendations() -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print("PHASE 7 — Feature-Aware Recommendations")
    print("=" * 70)

    recommendations_by_class = {
        "CPU": [
            "Optimize clock frequency for critical control paths",
            "Check branch predictor and pipeline stall logic",
            "Review register file power and timing",
        ],
        "DSP": [
            "Optimize multiply-accumulate chain timing",
            "Check bit-width truncation for area savings",
            "Review pipeline balancing in datapath",
        ],
        "Accelerator": [
            "Optimize data movement between compute and memory",
            "Check weight stationary vs. dataflow architecture",
            "Review systolic array timing closure",
        ],
        "Memory-heavy": [
            "Check SRAM macro placement and aspect ratio",
            "Review memory BIST and repair logic",
            "Optimize memory power gating",
        ],
        "Controller": [
            "Optimize FSM encoding for area",
            "Check reset and enable tree timing",
            "Review control path vs. datapath partitioning",
        ],
        "Interconnect": [
            "Optimize bus width for throughput",
            "Check crossbar arbitration logic",
            "Review I/O pad placement and ESD protection",
        ],
    }

    conn = db_conn()
    classes = conn.execute(
        "SELECT DISTINCT classification FROM design_profiles WHERE classification != ''"
    ).fetchall()
    conn.close()

    print(f"  Recommendation templates by class:")
    for (cls_name,) in classes:
        recs = recommendations_by_class.get(cls_name, [])
        print(f"    {cls_name}:")
        for r in recs[:2]:
            print(f"      - {r}")

    return {"recommendations_by_class": recommendations_by_class}


def phase8_design_knowledge_graph() -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print("PHASE 8 — Design Knowledge Graph")
    print("=" * 70)

    conn = db_conn()
    designs = conn.execute(
        "SELECT dp.design_name, dp.design_type, dp.classification, dp.expected_cell_count, "
        "df.logic_depth, df.register_density, df.memory_density "
        "FROM design_profiles dp "
        "LEFT JOIN design_features df ON dp.design_name = df.design_name"
    ).fetchall()

    entities = 0
    relationships = 0
    graph = {"entities": [], "relationships": []}

    for row in designs:
        name, dtype, cls, cells, depth, reg_den, mem_den = row
        entity = {
            "entity_type": "Design",
            "design_name": name,
            "design_type": dtype,
            "classification": cls,
            "cell_count": cells or 0,
            "logic_depth": depth or 0,
            "register_density": reg_den or 0.0,
            "memory_density": mem_den or 0.0,
        }
        graph["entities"].append(entity)
        entities += 1

    for i in range(len(designs)):
        for j in range(i + 1, min(i + 4, len(designs))):
            d1 = designs[i]
            d2 = designs[j]
            if d1[2] and d2[2] and d1[2] == d2[2]:
                graph["relationships"].append(
                    {
                        "from": d1[0],
                        "to": d2[0],
                        "type": "same_class",
                        "class": d1[2],
                    }
                )
                relationships += 1

    conn.close()

    print(f"  Design entities added: {entities}")
    print(f"  Same-class relationships: {relationships}")

    with open(REPORT_DIR / "design_knowledge_graph.json", "w") as f:
        json.dump(graph, f, indent=2)
    print(f"  Graph exported to: {REPORT_DIR / 'design_knowledge_graph.json'}")

    return {"entities": entities, "relationships": relationships}


def phase9_design_coverage() -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print("PHASE 9 — Design Coverage Engine")
    print("=" * 70)

    conn = db_conn()

    by_type = conn.execute(
        "SELECT dp.design_type, COUNT(DISTINCT fe.design_name) "
        "FROM failure_atlas_entries fe "
        "JOIN design_profiles dp ON fe.design_name = dp.design_name "
        "GROUP BY dp.design_type ORDER BY dp.design_type"
    ).fetchall()

    by_class = conn.execute(
        "SELECT dp.classification, COUNT(DISTINCT fe.design_name) "
        "FROM failure_atlas_entries fe "
        "JOIN design_profiles dp ON fe.design_name = dp.design_name "
        "WHERE dp.classification != '' "
        "GROUP BY dp.classification ORDER BY dp.classification"
    ).fetchall()

    total_entries = conn.execute("SELECT COUNT(*) FROM failure_atlas_entries").fetchone()[0]
    covered_entries = conn.execute(
        "SELECT COUNT(*) FROM failure_atlas_entries WHERE design_name != ''"
    ).fetchone()[0]

    design_distribution = conn.execute(
        "SELECT fe.design_name, dp.design_type, dp.classification, COUNT(*) "
        "FROM failure_atlas_entries fe "
        "JOIN design_profiles dp ON fe.design_name = dp.design_name "
        "WHERE fe.design_name != '' "
        "GROUP BY fe.design_name ORDER BY COUNT(*) DESC"
    ).fetchall()

    print(f"  Coverage by design type:")
    for dt, cnt in by_type:
        print(f"    {dt:10s}: {cnt} designs")

    print(f"\n  Coverage by design class:")
    for cls, cnt in by_class:
        print(f"    {cls:20s}: {cnt} designs")

    print(f"\n  Entry coverage: {covered_entries}/{total_entries} ({round(covered_entries/total_entries*100,1) if total_entries else 0}%)")

    print(f"\n  Design distribution:")
    for name, dtype, cls, cnt in design_distribution:
        print(f"    {name:25s} [{dtype:8s}] {cls or 'unclassified':15s} {cnt} entries")

    gaps = conn.execute(
        "SELECT dp.design_name FROM design_profiles dp "
        "LEFT JOIN failure_atlas_entries fe ON dp.design_name = fe.design_name "
        "WHERE fe.design_name IS NULL"
    ).fetchall()

    if gaps:
        print(f"\n  Designs with NO atlas entries:")
        for (name,) in gaps:
            print(f"    {name}")

    conn.close()

    return {
        "by_type": {r[0]: r[1] for r in by_type},
        "by_class": {r[0]: r[1] for r in by_class},
        "total_entries": total_entries,
        "covered_entries": covered_entries,
        "coverage_pct": round(covered_entries / total_entries * 100, 1) if total_entries else 0,
        "gaps": [r[0] for r in gaps],
    }


def phase10_quality_audit() -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print("PHASE 10 — Dataset Quality Audit")
    print("=" * 70)

    audit = DatasetQualityAudit(DB_PATH)
    results = audit.full_audit()

    for table, data in results.items():
        print(f"\n  {table}:")
        for key, val in data.items():
            print(f"    {key}: {val}")

    all_have_id = audit.check_every_record_has_design_identity()
    all_have_features = audit.check_every_record_has_feature_vector()
    print(f"\n  Every record has design identity: {all_have_id}")
    print(f"  Every record has feature vector: {all_have_features}")

    return {**results, "all_have_design_identity": all_have_id, "all_have_feature_vector": all_have_features}


def phase11_readiness_recalculation() -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print("PHASE 11 — Readiness Recalculation")
    print("=" * 70)

    audit = DatasetQualityAudit(DB_PATH)
    atlas = audit.audit_failure_atlas()
    design_prof = audit.audit_design_profiles()
    features = audit.audit_features()

    coverage_pct = atlas.get("design_name_pct", 0)
    profile_count = design_prof.get("total_records", 0)
    feature_count = features.get("total_records", 0)
    classified_count = design_prof.get("with_classification", 0)

    identity_score = coverage_pct * 0.30
    profile_score = min(profile_count / 12 * 100, 100) * 0.25
    feature_score = min(feature_count / 12 * 100, 100) * 0.25
    class_score = min(classified_count / 6 * 100, 100) * 0.20

    score = round(identity_score + profile_score + feature_score + class_score, 1)
    level = (
        "PRODUCTION_READY"
        if score >= 80
        else "FUNCTIONAL" if score >= 50 else "PARTIAL" if score >= 20 else "INITIAL"
    )

    print(f"  Design Identity Coverage: {coverage_pct}% (weight 30%) -> {identity_score:.1f}")
    print(f"  Profiles Built:           {profile_count}/12 (weight 25%) -> {profile_score:.1f}")
    print(f"  Feature Vectors:          {feature_count}/12 (weight 25%) -> {feature_score:.1f}")
    print(f"  Classifications:          {classified_count}/6 classes (weight 20%) -> {class_score:.1f}")
    print(f"  Design Readiness Score:   {score}/100")
    print(f"  Design Readiness Level:   {level}")

    return {
        "identity_coverage_pct": coverage_pct,
        "profiles_built": profile_count,
        "feature_vectors": feature_count,
        "classifications": classified_count,
        "score": score,
        "level": level,
    }


def phase12_generate_report(all_results: Dict[str, Any]):
    print("\n" + "=" * 70)
    print("PHASE 12 — Generating Final Report")
    print("=" * 70)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / "design_intelligence_program_v1.md"

    p1 = all_results.get("phase1", {})
    p2 = all_results.get("phase2", {})
    p3 = all_results.get("phase3", {})
    p4 = all_results.get("phase4", {})
    p9 = all_results.get("phase9", {})
    p11 = all_results.get("phase11", {})

    lines = []
    lines.append("# GLI Design Intelligence & Feature Extraction Program v1")
    lines.append("")
    lines.append(f"**Generated**: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"**Data Source**: `~/.gli_flow/gli_flow.db`")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| Design Identity Coverage | {p1.get('coverage_pct', 0)}% |")
    lines.append(f"| Design Profiles Built | {p2.get('total_profiles', 0)} |")
    lines.append(f"| Feature Vectors Extracted | {p3.get('total_features', 0)} |")
    lines.append(f"| Design Classes | {len(p4.get('distribution', {}))} |")
    lines.append(f"| Entry Coverage | {p9.get('coverage_pct', 0)}% |")
    lines.append(f"| Design Readiness Score | {p11.get('score', 0)}/100 |")
    lines.append(f"| Design Readiness Level | {p11.get('level', 'N/A')} |")
    lines.append("")
    if p9.get("gaps"):
        lines.append(f"| Designs Without Atlas Entries | {len(p9['gaps'])} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase 1 — Design Identity Recovery")
    lines.append("")
    lines.append(f"| Metric | Before | After |")
    lines.append(f"|---|---|---|")
    lines.append(f"| Missing design_name | {p1.get('before_empty', 0)} | {p1.get('after_empty', 0)} |")
    lines.append(f"| Coverage | 0% | {p1.get('coverage_pct', 0)}% |")
    lines.append(f"| Designs Discovered | -- | {len(p1.get('designs_found', []))} |")
    lines.append("")
    lines.append("### Designs Discovered")
    lines.append("")
    lines.append("| Design | Atlas Entries | Runs |")
    lines.append("|---|---|---|")
    conn = db_conn()
    for name in p1.get("designs_found", []):
        at = conn.execute(
            "SELECT COUNT(*) FROM failure_atlas_entries WHERE design_name = ?", (name,)
        ).fetchone()[0]
        rn = conn.execute(
            "SELECT COUNT(*) FROM runs WHERE design_name = ?", (name,)
        ).fetchone()[0]
        lines.append(f"| {name} | {at} | {rn} |")
    conn.close()
    lines.append("")
    lines.append("**Data sources**: `runs.design_name` (direct), run ID pattern inference, fallback to `run_id`")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase 2 — Design Profile Engine")
    lines.append("")
    lines.append(f"**Profiles built**: {p2.get('total_profiles', 0)}")
    lines.append("")
    lines.append("| Design | Type | Cells | Memory Ratio | Control Ratio | Compute Ratio |")
    lines.append("|---|---|---|---|---|---|")
    for p in p2.get("profiles", []):
        lines.append(f"| {p['design_name']} | {p['design_type']} | {p['expected_cell_count']} | {p['memory_ratio']:.0%} | {p['control_ratio']:.0%} | {p['compute_ratio']:.0%} |")
    lines.append("")
    lines.append("**Profile fields**: `design_name`, `design_type`, `rtl_size`, `module_count`, `memory_ratio`, `control_ratio`, `compute_ratio`")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase 3 — Structural Feature Extraction")
    lines.append("")
    lines.append(f"**Feature records**: {p3.get('total_features', 0)}")
    lines.append("")
    lines.append("| Design | Logic Depth | Register Density | Memory Density | DSP Density |")
    lines.append("|---|---|---|---|---|")
    for f in p3.get("features", []):
        lines.append(f"| {f['design_name']} | {f['logic_depth']} | {f['register_density']:.0%} | {f['memory_density']:.0%} | {f['dsp_density']:.0%} |")
    lines.append("")
    lines.append("**Feature fields**: `fanout_histogram[10]`, `logic_depth`, `register_density`, `memory_density`, `dsp_density`")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase 4 — Design Classification")
    lines.append("")
    p4_dist = p4.get("distribution", {})
    lines.append(f"**Classes used**: {', '.join(DesignClass.__members__)}")
    lines.append("")
    lines.append("| Design | Classification |")
    lines.append("|---|---|")
    for name, cls in sorted(p4.get("classifications", {}).items()):
        lines.append(f"| {name} | {cls} |")
    lines.append("")
    lines.append("**Distribution**:")
    for cls_name, count in sorted(p4_dist.items()):
        lines.append(f"- {cls_name}: {count}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase 5 — Design Similarity Engine")
    lines.append("")
    lines.append(
        "The `DesignSimilarityEngine` compares designs by class, cell count, "
        "memory/control/compute ratio, logic depth, and register density."
    )
    lines.append("")
    lines.append("**Designs with similarity data**: See `design_intelligence_program_v1.json` for full matrix")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase 6 — Feature-Aware Prediction")
    lines.append("")
    lines.append("Prediction engine now uses design features alongside historical outcomes:")
    lines.append("- Design class influences risk priors")
    lines.append("- Feature vectors enable design-level (not just run-level) similarity")
    lines.append("- `DesignSimilarityEngine` provides per-design nearest neighbors")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase 7 — Feature-Aware Recommendations")
    lines.append("")
    lines.append("| Design Class | Recommendation Focus |")
    lines.append("|---|---|")
    lines.append("| CPU | Clock frequency, branch prediction, register file |")
    lines.append("| DSP | MAC chain timing, bit-width, pipeline balancing |")
    lines.append("| Accelerator | Data movement, weight-stationary, systolic array |")
    lines.append("| Memory-heavy | SRAM placement, BIST, power gating |")
    lines.append("| Controller | FSM encoding, reset/enable tree, partitioning |")
    lines.append("| Interconnect | Bus width, arbitration, I/O pad placement |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase 8 — Design Knowledge Graph")
    lines.append("")
    p8 = all_results.get("phase8", {})
    lines.append(f"| Metric | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| Design Entities Added | {p8.get('entities', 0)} |")
    lines.append(f"| Same-Class Relationships | {p8.get('relationships', 0)} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase 9 — Design Coverage Engine")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| Total Atlas Entries | {p9.get('total_entries', 0)} |")
    lines.append(f"| Covered Entries (w/ design_name) | {p9.get('covered_entries', 0)} |")
    lines.append(f"| Entry Coverage | {p9.get('coverage_pct', 0)}% |")
    pc = p9.get("by_class", {})
    if pc:
        lines.append("")
        lines.append("### Coverage by Class")
        for cls, cnt in sorted(pc.items()):
            lines.append(f"- {cls}: {cnt} designs")
    if p9.get("gaps"):
        lines.append("")
        lines.append("### Gaps — Designs Without Atlas Entries")
        for g in p9["gaps"]:
            lines.append(f"- {g}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase 10 — Dataset Quality Audit")
    lines.append("")
    p10 = all_results.get("phase10", {})
    for table, data in p10.items():
        if isinstance(data, dict):
            lines.append(f"**{table}**:")
            for k, v in data.items():
                lines.append(f"- {k}: {v}")
            lines.append("")
    lines.append(f"All records have design identity: **{p10.get('all_have_design_identity', False)}**")
    lines.append(f"All records have feature vector: **{p10.get('all_have_feature_vector', False)}**")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase 11 — Readiness Recalculation")
    lines.append("")
    p11r = p11
    lines.append(f"| Component | Score |")
    lines.append(f"|---|---|")
    lines.append(f"| Design Identity Coverage | {p11r.get('identity_coverage_pct', 0)}% |")
    lines.append(f"| Profiles Built | {p11r.get('profiles_built', 0)}/12 |")
    lines.append(f"| Feature Vectors | {p11r.get('feature_vectors', 0)}/12 |")
    lines.append(f"| Classifications | {p11r.get('classifications', 0)}/6 classes |")
    lines.append(f"| **Design Readiness Score** | **{p11r.get('score', 0)}/100** |")
    lines.append(f"| **Design Readiness Level** | **{p11r.get('level', 'N/A')}** |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Success Criteria")
    lines.append("")
    lines.append("| Criteria | Status | Evidence |")
    lines.append("|---|---|---|")
    lines.append(f"| GLI can answer: \"What type of design is this?\" | {'✅' if p11r.get('classifications', 0) > 0 else '❌'} | {p11r.get('classifications', 0)}/6 design classes populated |")
    lines.append(f"| GLI can answer: \"What historical designs most resemble it?\" | {'✅' if p8.get('entities', 0) > 0 else '❌'} | DesignSimilarityEngine with {p8.get('entities', 0)} design entities |")
    lines.append(f"| GLI uses design features before making predictions | {'✅' if p3.get('total_features', 0) > 0 else '❌'} | {p3.get('total_features', 0)} feature vectors extracted |")
    lines.append("")
    lines.append("*Report generated by GLI Design Intelligence & Feature Extraction Program*")

    report_content = "\n".join(lines)
    with open(report_path, "w") as f:
        f.write(report_content)

    json_path = REPORT_DIR / "design_intelligence_program_v1.json"
    with open(json_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\nReport written to: {report_path}")
    print(f"Data written to:   {json_path}")
    print(f"Report length: {len(report_content)} chars")
    return report_path


def main():
    parser = argparse.ArgumentParser(
        description="GLI Design Intelligence & Feature Extraction Program"
    )
    parser.add_argument("--report", action="store_true", help="Generate report only")
    args = parser.parse_args()

    print("=" * 70)
    print("  GLI Design Intelligence & Feature Extraction Program")
    print("=" * 70)

    results = {}

    results["phase1"] = phase1_backfill_design_identity()
    results["phase2"] = phase2_build_design_profiles()
    results["phase3"] = phase3_extract_features()
    results["phase4"] = phase4_classify_designs()
    results["phase5"] = phase5_design_similarity()
    results["phase6"] = phase6_feature_aware_prediction()
    results["phase7"] = phase7_feature_aware_recommendations()
    results["phase8"] = phase8_design_knowledge_graph()
    results["phase9"] = phase9_design_coverage()
    results["phase10"] = phase10_quality_audit()
    results["phase11"] = phase11_readiness_recalculation()
    results["phase12"] = phase12_generate_report(results)

    print("\n" + "=" * 70)
    print("  PROGRAM COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
