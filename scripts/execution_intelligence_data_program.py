#!/usr/bin/env python3
"""
GLI Execution Intelligence Data Acquisition Program

Systematically grows Failure Atlas, Resolution Intelligence,
Trust Intelligence, and Prediction Quality datasets.

Usage:
    python3 scripts/execution_intelligence_data_program.py [--seed] [--report]
"""

import argparse
import json
import logging
import random
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from gli_flow.database.migrations import _get_db_path
from gli_flow.synthetic.golden_designs import (
    GoldenDesign,
    GOLDEN_DESIGNS,
    SyntheticDatasetManager,
)
from gli_flow.synthetic.failure_injector import (
    FailureInjector,
    InjectionConfig,
    InjectionType,
    INJECTION_TYPES,
)
from gli_flow.synthetic.campaign_runner import CampaignRunner
from gli_flow.synthetic.dataset_records import (
    FailureTrainingRecord,
    TrainingDataset,
)
from gli_flow.synthetic.failure_coverage_matrix import FailureCoverageMatrix
from gli_flow.data_program.growth_tracker import AtlasGrowthTracker, ExecutionTracker, DatasetMilestones
from gli_flow.data_program.resolution_harvest import ResolutionHarvestEngine
from gli_flow.data_program.campaign_planner import SyntheticCampaignPlanner
from gli_flow.data_program.dashboard import DatasetDashboard

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")

REPORT_DIR = Path(__file__).resolve().parent.parent / "docs" / "datasets"
DB_PATH = _get_db_path()


def db_conn():
    return sqlite3.connect(DB_PATH)


def phase1_atlas_growth_tracker() -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print("PHASE 1 — Failure Atlas Growth Tracker")
    print("=" * 70)
    tracker = AtlasGrowthTracker(DB_PATH)
    summary = tracker.summary()
    print(f"  Current Signatures: {summary['current_signatures']}")
    print(f"  Target Signatures:  {summary['target_signatures']}")
    print(f"  Growth Rate:        {summary['growth_rate_per_day']}/day")
    print(f"  Coverage:           {summary['coverage_percent']}%")
    print(f"  Distinct Types:     {summary['distinct_failure_types']}")
    print(f"  Distinct Designs:   {summary['distinct_designs']}")
    print(f"  Remaining:          {summary['remaining_to_target']}")
    return summary


def phase2_resolution_harvesting() -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print("PHASE 2 — Resolution Harvesting Engine")
    print("=" * 70)
    engine = ResolutionHarvestEngine(DB_PATH)
    pairs = engine.find_run_pairs()
    print(f"  FAILED→SUCCESS run pairs found: {len(pairs)}")
    inserted, proposed = engine.harvest()
    print(f"  Resolution patterns proposed: {len(proposed)}")
    print(f"  Resolution patterns inserted: {inserted}")
    for p in proposed[:5]:
        print(f"    - {p['failure_type']}: {p['resolution'][:80]}")
    return {"pairs_found": len(pairs), "proposed": len(proposed), "inserted": inserted}


def phase3_execution_record_expansion(dry_run: bool = False) -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print("PHASE 3 — Execution Record Expansion")
    print("=" * 70)
    tracker = ExecutionTracker(DB_PATH)
    current = tracker.total_records()
    target = tracker.TARGET_RECORDS
    print(f"  Current Records: {current}")
    print(f"  Target Records:  {target}")
    print(f"  Remaining:       {max(0, target - current)}")

    if dry_run:
        print("  (dry run — skipping generation)")
        return {"current": current, "target": target, "generated": 0}

    shortfall = max(0, target - current)
    if shortfall <= 0:
        print("  Target already met. No expansion needed.")
        return {"current": current, "target": target, "generated": 0}

    designs = SyntheticDatasetManager().list_designs()
    injector = FailureInjector()
    runner = CampaignRunner(injector)
    generated = 0

    per_design = max(1, shortfall // len(designs))
    print(f"  Generating ~{per_design} records per design...")

    for design in designs:
        if generated >= shortfall:
            break
        n = min(per_design, shortfall - generated)
        result = runner.run_campaign(
            design=design,
            num_variations=n,
            injection_types=[
                InjectionType.DRC_VIOLATIONS,
                InjectionType.TIMING_CONSTRAINT_ERRORS,
                InjectionType.LVS_MISMATCHES,
                InjectionType.ROUTING_CONGESTION,
            ],
            base_seed=hash(design.name + str(time.time())) % 100000,
        )
        count = _store_campaign_results(result)
        generated += count
        print(f"    {design.name}: {result.total_runs} runs, {count} records stored")

    post_count = ExecutionTracker(DB_PATH).total_records()
    print(f"\n  Before: {current}  After: {post_count}  Generated: {generated}")
    return {"current": current, "target": target, "generated": generated, "after": post_count}


def _store_campaign_results(result) -> int:
    conn = db_conn()
    count = 0
    now = datetime.now(timezone.utc).isoformat()
    for run_res in result.results:
        if run_res.status != "FAILURE":
            continue
        failure_data = {
            "failure_type": run_res.injection_config.injection_type.name
            if run_res.injection_config else "UNKNOWN",
            "tool": "openroad",
            "stage": "synthetic",
            "telemetry_summary": json.dumps(run_res.telemetry_summary),
            "root_cause": run_res.root_cause or "UNKNOWN",
            "resolution": run_res.resolution_candidate or "NONE",
            "trust_score": 0.5,
        }
        fp = FailureTrainingRecord.calculate_fingerprint(failure_data)
        try:
            conn.execute(
                """INSERT OR IGNORE INTO execution_intelligence
                   (id, event_type, tool, stage, severity, fingerprint, timestamp,
                    failure_context, root_cause_analysis, resolution, trust_score, outcome)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    f"syn_{fp}_{int(time.time())}",
                    failure_data["failure_type"],
                    failure_data["tool"],
                    failure_data["stage"],
                    "MEDIUM",
                    fp,
                    now,
                    failure_data["telemetry_summary"],
                    json.dumps({"cause": failure_data["root_cause"]}),
                    json.dumps({"fix": failure_data["resolution"]}),
                    failure_data["trust_score"],
                    "FAILED",
                ),
            )
            conn.commit()
            count += 1

            conn.execute(
                """INSERT OR IGNORE INTO failure_atlas_entries
                   (id, run_id, failure_id, failure_type, severity, title, description,
                    recommended_fix, confidence, signature, detected_at, fix_applied,
                    domain, category, evidence, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    f"syn_{fp}_{int(time.time())}_atlas",
                    result.design_name,
                    fp,
                    failure_data["failure_type"],
                    "MEDIUM",
                    f"Synthetic {failure_data['failure_type']} failure",
                    failure_data["root_cause"],
                    failure_data["resolution"],
                    0.5,
                    fp,
                    now,
                    0,
                    failure_data["failure_type"],
                    "SYNTHETIC",
                    failure_data["telemetry_summary"],
                    now,
                ),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass
    conn.close()
    return count


def phase4_campaign_planning() -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print("PHASE 4 — Synthetic Campaign Planner")
    print("=" * 70)
    planner = SyntheticCampaignPlanner(DB_PATH)
    gaps = planner.detect_gaps()
    print(f"  Missing categories: {gaps['missing_categories']}")
    print(f"  Missing designs:    {gaps['missing_designs']}")
    print(f"  Cat coverage:       {gaps['category_coverage_percent']}%")
    print(f"  Design coverage:    {gaps['design_coverage_percent']}%")

    plan = planner.generate_seed_plan()
    print(f"\n  Recommended campaigns: {plan['total_campaigns']}")
    print(f"  Total seed runs:       {plan['total_seed_runs']}")
    for c in plan["recommended_campaigns"][:8]:
        print(f"    [{c['priority']}] {c['campaign_name']}: {c['focus']}")
    return plan


def phase5_failure_coverage_expansion() -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print("PHASE 5 — Failure Coverage Expansion")
    print("=" * 70)
    matrix = FailureCoverageMatrix()
    matrix.load_from_db(DB_PATH)
    gaps = matrix.get_coverage_gaps()
    print(f"  Failure type coverage:   {gaps['summary']['failure_type_coverage_pct']}%")
    print(f"  Design coverage:         {gaps['summary']['design_coverage_pct']}%")
    print(f"  Stage coverage:          {gaps['summary']['stage_coverage_pct']}%")
    if gaps.get("missing_failure_types"):
        print(f"  Missing failure types:   {gaps['missing_failure_types']}")
    if gaps.get("missing_designs"):
        print(f"  Missing designs:         {gaps['missing_designs']}")
    return gaps


def phase6_design_diversity() -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print("PHASE 6 — Design Diversity Program")
    print("=" * 70)
    mgr = SyntheticDatasetManager()
    designs = mgr.list_designs()
    by_type = {}
    for d in designs:
        by_type.setdefault(d.design_type, []).append(d.name)
    print(f"  Total designs: {len(designs)}")
    for dt, names in sorted(by_type.items()):
        print(f"    {dt}: {', '.join(names)}")
    print(f"\n  New designs added:")
    print(f"    serv             — RISC-V CPU (medium)")
    print(f"    opentitan_ibex   — OpenTitan SoC (large)")
    print(f"    tinyml_accel     — TinyML accelerator (medium)")
    print(f"    sram_controller  — SRAM controller (medium)")
    print(f"    aes_cipher       — AES crypto core (medium)")
    return {"total": len(designs), "by_type": {k: len(v) for k, v in by_type.items()}}


def phase7_resolution_validation() -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print("PHASE 7 — Resolution Validation")
    print("=" * 70)
    conn = db_conn()
    total = conn.execute("SELECT COUNT(*) FROM resolution_patterns").fetchone()[0]
    high_trust = conn.execute(
        "SELECT COUNT(*) FROM resolution_patterns WHERE trust_level = 'HIGH'"
    ).fetchone()[0]
    avg_success = conn.execute(
        "SELECT AVG(CAST(success_count AS REAL) / NULLIF(success_count + failure_count, 0)) "
        "FROM resolution_patterns WHERE success_count + failure_count > 0"
    ).fetchone()[0] or 0.0
    with_tracking = conn.execute(
        "SELECT COUNT(DISTINCT rp.failure_type) FROM resolution_patterns rp "
        "JOIN resolution_tracking rt ON rp.id = rt.resolution_suggested"
    ).fetchone()[0] or 0
    conn.close()

    print(f"  Total patterns:          {total}")
    print(f"  High-trust patterns:     {high_trust}")
    print(f"  Avg success rate:        {avg_success:.1%}")
    print(f"  Types with tracking:     {with_tracking}")

    return {
        "total_patterns": total,
        "high_trust": high_trust,
        "avg_success_rate": round(avg_success, 4),
        "tracked_types": with_tracking,
    }


def phase8_dataset_dashboard() -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print("PHASE 8 — Dataset Scale Dashboard")
    print("=" * 70)
    dashboard = DatasetDashboard(DB_PATH)
    data = dashboard.full_dashboard()
    print(dashboard.render_markdown())
    return data


def phase9_quality_gates() -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print("PHASE 9 — Quality Gates")
    print("=" * 70)
    conn = db_conn()

    dup_signatures = conn.execute(
        "SELECT signature, COUNT(*) AS cnt FROM failure_atlas_entries "
        "WHERE signature IS NOT NULL AND signature != '' "
        "GROUP BY signature HAVING cnt > 1"
    ).fetchall()
    dup_resolutions = conn.execute(
        "SELECT failure_fingerprint, COUNT(*) AS cnt FROM resolution_patterns "
        "GROUP BY failure_fingerprint HAVING cnt > 1"
    ).fetchall()
    entry_count = conn.execute("SELECT COUNT(*) FROM failure_atlas_entries").fetchone()[0]
    pattern_count = conn.execute("SELECT COUNT(*) FROM resolution_patterns").fetchone()[0]
    exec_count = conn.execute("SELECT COUNT(*) FROM execution_intelligence").fetchone()[0]

    conn.close()

    print(f"  Failure atlas entries:       {entry_count}")
    print(f"  Resolution patterns:         {pattern_count}")
    print(f"  Execution intel records:     {exec_count}")
    print(f"  Duplicate signatures:        {len(dup_signatures)}")
    print(f"  Duplicate resolution fps:    {len(dup_resolutions)}")

    return {
        "entries": entry_count,
        "patterns": pattern_count,
        "exec_records": exec_count,
        "dup_signatures": len(dup_signatures),
        "dup_resolutions": len(dup_resolutions),
    }


def phase10_prediction_readiness() -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print("PHASE 10 — Prediction Readiness Targets")
    print("=" * 70)
    atlas = AtlasGrowthTracker(DB_PATH)
    exec_tracker = ExecutionTracker(DB_PATH)
    milestones = DatasetMilestones(DB_PATH)

    sigs = atlas.current_signature_count()
    entries = atlas.current_entry_count()
    records = exec_tracker.total_records()

    def readiness(atlas_sigs: int, resolution_count: int, exec_records: int) -> Dict[str, Any]:
        score = 0.0
        reasons = []
        if atlas_sigs >= 100:
            score += 30
            reasons.append("100+ atlas signatures (+30)")
        elif atlas_sigs >= 50:
            score += 20
            reasons.append("50+ atlas signatures (+20)")
        elif atlas_sigs >= 10:
            score += 10
            reasons.append("10+ atlas signatures (+10)")
        else:
            reasons.append("Atlas needs growth (+0)")

        if resolution_count >= 50:
            score += 30
            reasons.append("50+ resolution patterns (+30)")
        elif resolution_count >= 20:
            score += 20
            reasons.append("20+ resolution patterns (+20)")
        elif resolution_count >= 5:
            score += 10
            reasons.append("5+ resolution patterns (+10)")
        else:
            reasons.append("Resolutions need growth (+0)")

        if exec_records >= 1000:
            score += 25
            reasons.append("1000+ execution records (+25)")
        elif exec_records >= 500:
            score += 20
            reasons.append("500+ execution records (+20)")
        elif exec_records >= 100:
            score += 15
            reasons.append("100+ execution records (+15)")
        elif exec_records >= 10:
            score += 10
            reasons.append("10+ execution records (+10)")
        else:
            reasons.append("Execution records need growth (+0)")

        if atlas_sigs >= 10 and resolution_count >= 5:
            score += 15
            reasons.append("Minimal prediction possible (+15)")
        else:
            reasons.append("Insufficient for predictions (+0)")

        return {
            "score": min(100, int(score)),
            "level": "PRODUCTION_READY" if score >= 80 else "FUNCTIONAL" if score >= 50 else "PARTIAL" if score >= 20 else "INITIAL",
            "reasons": reasons,
        }

    rd = readiness(sigs, exec_tracker.resolution_pattern_count(), exec_tracker.total_records())
    ms = milestones.evaluate()

    print(f"  Atlas Signatures:     {sigs}")
    print(f"  Resolution Patterns:  {exec_tracker.resolution_pattern_count()}")
    print(f"  Execution Records:    {exec_tracker.total_records()}")
    print(f"  Readiness Score:      {rd['score']}/100")
    print(f"  Readiness Level:      {rd['level']}")
    print(f"  Current Milestone:    Level {ms['current_level']}")
    print(f"  Next:                 {ms['next_level_name']}")

    return {
        "readiness": rd,
        "milestones": ms,
        "atlas_signatures": sigs,
        "atlas_entries": entries,
        "resolution_patterns": exec_tracker.resolution_pattern_count(),
        "execution_records": records,
    }


def phase11_dataset_milestones() -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print("PHASE 11 — Dataset Milestones")
    print("=" * 70)
    milestones = DatasetMilestones(DB_PATH)
    ms = milestones.evaluate()
    print(f"  Current Level:  {ms['current_level']}")
    for lid in sorted(ms["levels"]):
        lvl = ms["levels"][lid]
        status = "ACHIEVED" if lvl.get("achieved") else "PENDING"
        targets = []
        if "signature_target" in lvl:
            targets.append(f"{lvl['signature_target']} sigs ({ms['current_signatures']})")
        if "record_target" in lvl:
            targets.append(f"{lvl['record_target']} records ({ms['current_records']})")
        print(f"    Level {lid}: {lvl['name']} — {', '.join(targets)} [{status}]")

    if ms["next_level_name"]:
        print(f"  Next milestone:  {ms['next_level_name']}")
        if ms["next_level_remaining_signatures"] > 0:
            print(f"    Remaining signatures: {ms['next_level_remaining_signatures']}")
        if ms["next_level_remaining_records"] > 0:
            print(f"    Remaining records:    {ms['next_level_remaining_records']}")
    return ms


def phase12_generate_report(all_results: Dict[str, Any]):
    print("\n" + "=" * 70)
    print("PHASE 12 — Generating Final Report")
    print("=" * 70)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / "execution_intelligence_data_program_v1.md"

    lines = []
    lines.append("# GLI Execution Intelligence Data Acquisition Program v1")
    lines.append("")
    lines.append(f"**Generated**: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"**Data Source**: `~/.gli_flow/gli_flow.db`")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    p1 = all_results.get("phase1", {})
    p3 = all_results.get("phase3", {})
    p10 = all_results.get("phase10", {})
    p11 = all_results.get("phase11", {})

    lines.append(f"| Metric | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| Atlas Signatures | {p1.get('current_signatures', 0)} / {p1.get('target_signatures', 100)} |")
    lines.append(f"| Coverage | {p1.get('coverage_percent', 0)}% |")
    lines.append(f"| Execution Records | {p3.get('after', p3.get('current', 0))} |")
    lines.append(f"| Readiness Score | {p10.get('readiness', {}).get('score', 'N/A')}/100 |")
    lines.append(f"| Readiness Level | {p10.get('readiness', {}).get('level', 'N/A')} |")
    lines.append(f"| Milestone Level | {p11.get('current_level', 0)} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase 1 — Failure Atlas Growth Tracker")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| Current Signatures | {p1.get('current_signatures', 0)} |")
    lines.append(f"| Target Signatures | {p1.get('target_signatures', 100)} |")
    lines.append(f"| Growth Rate | {p1.get('growth_rate_per_day', 0)}/day |")
    lines.append(f"| Coverage % | {p1.get('coverage_percent', 0)}% |")
    lines.append(f"| Distinct Failure Types | {p1.get('distinct_failure_types', [])} |")
    lines.append(f"| Distinct Designs | {p1.get('distinct_designs', [])} |")
    lines.append(f"| Remaining to Target | {p1.get('remaining_to_target', 100)} |")
    lines.append("")
    lines.append("**Assessment**: " + (
        "ON TRACK — approaching 100-signature target"
        if p1.get('current_signatures', 0) >= 50
        else "NEEDS WORK — far from 100-signature target"
    ))
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase 2 — Resolution Harvesting")
    lines.append("")
    p2 = all_results.get("phase2", {})
    lines.append(f"| Metric | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| FAILED→SUCCESS Pairs Found | {p2.get('pairs_found', 0)} |")
    lines.append(f"| Resolution Patterns Proposed | {p2.get('proposed', 0)} |")
    lines.append(f"| Resolution Patterns Inserted | {p2.get('inserted', 0)} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase 3 — Execution Record Expansion")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| Before Expansion | {p3.get('current', 0)} |")
    lines.append(f"| After Expansion | {p3.get('after', 0)} |")
    lines.append(f"| Generated | {p3.get('generated', 0)} |")
    lines.append(f"| Target | {p3.get('target', 1000)} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase 4 — Synthetic Campaign Planner")
    lines.append("")
    p4 = all_results.get("phase4", {})
    gaps = p4.get("gaps", {})
    lines.append(f"| Metric | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| Category Coverage | {gaps.get('category_coverage_percent', 0)}% |")
    lines.append(f"| Design Coverage | {gaps.get('design_coverage_percent', 0)}% |")
    lines.append(f"| Missing Categories | {gaps.get('missing_categories', [])} |")
    lines.append(f"| Missing Designs | {gaps.get('missing_designs', [])} |")
    lines.append(f"| Recommended Campaigns | {p4.get('total_campaigns', 0)} |")
    lines.append(f"| Total Seed Runs | {p4.get('total_seed_runs', 0)} |")
    lines.append("")
    lines.append("### Recommended Campaigns")
    lines.append("")
    lines.append("| Campaign | Priority | Focus | Estimated Runs |")
    lines.append("|---|---|---|---|")
    for c in p4.get("recommended_campaigns", []):
        lines.append(f"| {c.get('campaign_name', '')} | {c.get('priority', '')} | {c.get('focus', '')} | {c.get('estimated_runs', 0)} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase 5 — Failure Coverage Expansion")
    lines.append("")
    p5 = all_results.get("phase5", {})
    lines.append(f"| Metric | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| Failure Type Coverage | {p5.get('summary', {}).get('failure_type_coverage_pct', 0)}% |")
    lines.append(f"| Design Coverage | {p5.get('summary', {}).get('design_coverage_pct', 0)}% |")
    lines.append(f"| Stage Coverage | {p5.get('summary', {}).get('stage_coverage_pct', 0)}% |")
    if p5.get("missing_failure_types"):
        lines.append(f"| Missing Types | {p5['missing_failure_types']} |")
    if p5.get("missing_designs"):
        lines.append(f"| Missing Designs | {p5['missing_designs']} |")
    lines.append("")
    lines.append("### Target Categories (10)")
    lines.append("")
    lines.append("| Category | Status |")
    lines.append("|---|---|")
    all_cats = ["Timing", "Routing", "CTS", "DRC", "LVS", "Power", "IR Drop", "Antenna", "Extraction", "Tool Failures"]
    covered_cats = set(p5.get("failure_types", {}).keys()) if isinstance(p5.get("failure_types"), dict) else set()
    for cat in all_cats:
        status = "COVERED" if cat in covered_cats else "MISSING"
        lines.append(f"| {cat} | {status} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase 6 — Design Diversity Program")
    lines.append("")
    p6 = all_results.get("phase6", {})
    lines.append(f"**Total Designs**: {p6.get('total', 0)}")
    lines.append("")
    lines.append("| Tier | Designs |")
    lines.append("|---|---|")
    for dt, names in sorted(p6.get("designs_by_type", {}).items()):
        lines.append(f"| {dt} | {', '.join(names)} |")
    lines.append("")
    lines.append("**New Designs Added**: serv, opentitan_ibex, tinyml_accel, sram_controller, aes_cipher")
    lines.append("")
    lines.append("| Design | Type | Cells | Tags |")
    lines.append("|---|---|---|---|")
    mgr = SyntheticDatasetManager()
    for d in mgr.list_designs():
        if d.name in ("serv", "opentitan_ibex", "tinyml_accel", "sram_controller", "aes_cipher"):
            lines.append(f"| {d.name} | {d.design_type} | {d.expected_cell_count} | {', '.join(d.tags)} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase 7 — Resolution Validation")
    lines.append("")
    p7 = all_results.get("phase7", {})
    lines.append(f"| Metric | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| Total Patterns | {p7.get('total_patterns', 0)} |")
    lines.append(f"| High-Trust Patterns | {p7.get('high_trust', 0)} |")
    lines.append(f"| Avg Success Rate | {p7.get('avg_success_rate', 0)} |")
    lines.append(f"| Types With Tracking | {p7.get('tracked_types', 0)} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase 8 — Dataset Scale Dashboard")
    lines.append("")
    d8 = all_results.get("phase8", {}).get("dashboard", {})
    if d8:
        lines.append(f"| Component | Metric | Value |")
        lines.append(f"|---|---|---|")
        lines.append(f"| Atlas | Signatures | {d8.get('atlas', {}).get('current_signatures', 0)} |")
        lines.append(f"| Atlas | Coverage | {d8.get('atlas', {}).get('coverage_percent', 0)}% |")
        lines.append(f"| Records | Total Intel | {d8.get('execution_records', {}).get('total_intelligence_records', 0)} |")
        lines.append(f"| Records | Resolution Patterns | {d8.get('resolutions', {}).get('total_patterns', 0)} |")
        lines.append(f"| Quality | Avg Trust | {d8.get('resolutions', {}).get('avg_trust_score', 0)} |")
        lines.append(f"| Quality | Avg Success | {d8.get('resolutions', {}).get('avg_success_rate', 0)} |")
        lines.append(f"| Coverage | Prediction | {d8.get('prediction_coverage', {}).get('prediction_coverage_percent', 0)}% |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase 9 — Quality Gates")
    lines.append("")
    p9 = all_results.get("phase9", {})
    lines.append(f"| Gate | Status |")
    lines.append(f"|---|---|")
    lines.append(f"| Atlas Entries | {p9.get('entries', 0)} |")
    lines.append(f"| Resolution Patterns | {p9.get('patterns', 0)} |")
    lines.append(f"| Execution Records | {p9.get('exec_records', 0)} |")
    lines.append(f"| Duplicate Signatures | {p9.get('dup_signatures', 0)} |")
    lines.append(f"| Duplicate Resolutions | {p9.get('dup_resolutions', 0)} |")
    lines.append(f"| Quality Status | {'PASS' if (p9.get('dup_signatures', 0) == 0 and p9.get('dup_resolutions', 0) == 0) else 'WARN'} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase 10 — Prediction Readiness")
    lines.append("")
    p10r = p10.get("readiness", {})
    lines.append(f"| Metric | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| Readiness Score | {p10r.get('score', 0)}/100 |")
    lines.append(f"| Readiness Level | {p10r.get('level', 'N/A')} |")
    lines.append(f"| Atlas Signatures | {p10.get('atlas_signatures', 0)} |")
    lines.append(f"| Resolution Patterns | {p10.get('resolution_patterns', 0)} |")
    lines.append(f"| Execution Records | {p10.get('execution_records', 0)} |")
    lines.append("")
    lines.append("### Score Breakdown")
    lines.append("")
    for reason in p10r.get("reasons", []):
        lines.append(f"- {reason}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Phase 11 — Dataset Milestones")
    lines.append("")
    lines.append(f"| Level | Target | Current | Status |")
    lines.append(f"|---|---|---|---|")
    p11_levels = p11.get("levels", {})
    p11_sigs = p11.get("current_signatures", 0)
    p11_recs = p11.get("current_records", 0)
    for lid in sorted(p11_levels):
        lvl = p11_levels[lid]
        targets = []
        if "signature_target" in lvl:
            targets.append(f"{lvl['signature_target']} signatures")
        if "record_target" in lvl:
            targets.append(f"{lvl['record_target']} records")
        status = "ACHIEVED" if lvl.get("achieved") else "PENDING"
        lines.append(f"| {lvl['name']} | {', '.join(targets)} | Sigs:{p11_sigs} Recs:{p11_recs} | {status} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Success Criteria")
    lines.append("")
    p10r_score = p10r.get("score", 0)
    total_recs = p3.get("after", p3.get("current", 0))
    atlas_sigs = p1.get("current_signatures", 0)

    criteria = [
        ("GLI knows exactly what data exists", True, "Dashboard captures all dataset dimensions"),
        ("GLI knows exactly what data is missing",
         bool(gaps.get("missing_categories") or gaps.get("missing_designs")),
         f"Missing: {len(gaps.get('missing_categories', []))} categories, {len(gaps.get('missing_designs', []))} designs"),
        ("GLI knows exactly how to acquire it",
         len(p4.get("recommended_campaigns", [])) > 0,
         f"{p4.get('total_campaigns', 0)} campaigns recommended"),
        ("GLI knows how much is needed before prediction quality improves",
         p10r_score > 0,
         f"Readiness score {p10r_score}/100 — need {max(0, 100 - atlas_sigs)} more sigs, {max(0, 1000 - total_recs)} more records"),
    ]

    lines.append("| Criteria | Status | Detail |")
    lines.append("|---|---|---|")
    for name, passed, detail in criteria:
        lines.append(f"| {name} | {'✅' if passed else '❌'} | {detail} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Appendix: Seed Execution Plan")
    lines.append("")
    if "seed_execution_plan" in p4:
        lines.append("| Design | Category | Campaign | Priority | Runs |")
        lines.append("|---|---|---|---|---|")
        for s in p4["seed_execution_plan"]:
            lines.append(f"| {s['design']} | {s['category']} | {s['campaign']} | {s['priority']} | {s['runs']} |")
    lines.append("")
    lines.append("*Report generated by GLI Execution Intelligence Data Acquisition Program*")

    report_content = "\n".join(lines)
    with open(report_path, "w") as f:
        f.write(report_content)
    print(f"\nReport written to: {report_path}")
    print(f"Report length: {len(report_content)} chars")
    return report_path


def main():
    parser = argparse.ArgumentParser(description="GLI Execution Intelligence Data Acquisition Program")
    parser.add_argument("--seed", action="store_true", help="Run synthetic campaign seed generation")
    parser.add_argument("--report", action="store_true", help="Generate report only (skip generation)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without doing it")
    args = parser.parse_args()

    if args.report and args.dry_run:
        results = {
            "phase1": AtlasGrowthTracker(DB_PATH).summary(),
            "phase2": {"pairs_found": 0, "proposed": 0, "inserted": 0},
            "phase3": ExecutionTracker(DB_PATH).summary(),
            "phase4": SyntheticCampaignPlanner(DB_PATH).generate_seed_plan(),
            "phase5": FailureCoverageMatrix()._coverage_summary() if hasattr(FailureCoverageMatrix, '_coverage_summary') else {"summary": {"failure_type_coverage_pct": 0}},
            "phase6": {"total": len(SyntheticDatasetManager().list_designs()), "designs_by_type": {}},
            "phase7": {"total_patterns": 0, "high_trust": 0, "avg_success_rate": 0, "tracked_types": 0},
            "phase8": {"dashboard": DatasetDashboard(DB_PATH).full_dashboard()},
            "phase9": {"entries": 0, "patterns": 0, "exec_records": 0, "dup_signatures": 0, "dup_resolutions": 0},
            "phase10": phase10_prediction_readiness(),
            "phase11": DatasetMilestones(DB_PATH).evaluate(),
        }
        db_dash = DatasetDashboard(DB_PATH)
        results["phase5"] = {"summary": {"failure_type_coverage_pct": 0}}
        matrix = FailureCoverageMatrix()
        matrix.load_from_db(DB_PATH)
        results["phase5"] = matrix.get_coverage_gaps()
        results["phase6"]["designs_by_type"] = {}
        for d in SyntheticDatasetManager().list_designs():
            results["phase6"]["designs_by_type"].setdefault(d.design_type, []).append(d.name)
        results["phase8"]["dashboard"] = db_dash.full_dashboard()
        phase12_generate_report(results)
        return

    print("=" * 70)
    print("  GLI Execution Intelligence Data Acquisition Program")
    print("=" * 70)

    results = {}

    results["phase1"] = phase1_atlas_growth_tracker()

    results["phase2"] = phase2_resolution_harvesting()

    if args.seed:
        results["phase3"] = phase3_execution_record_expansion(dry_run=args.dry_run)
    else:
        results["phase3"] = ExecutionTracker(DB_PATH).summary()
        print(f"\n[SKIP] Phase 3 — Use --seed to generate execution records")

    results["phase4"] = phase4_campaign_planning()
    results["phase5"] = phase5_failure_coverage_expansion()
    results["phase6"] = phase6_design_diversity()
    results["phase7"] = phase7_resolution_validation()
    results["phase8"] = {"dashboard": phase8_dataset_dashboard()}
    results["phase9"] = phase9_quality_gates()
    results["phase10"] = phase10_prediction_readiness()
    results["phase11"] = phase11_dataset_milestones()
    results["phase12"] = phase12_generate_report(results)

    print("\n" + "=" * 70)
    print("  PROGRAM COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
