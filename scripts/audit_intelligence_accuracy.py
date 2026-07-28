#!/usr/bin/env python3
"""
Intelligence Accuracy & Trustworthiness Audit.

Reads real data from SQLite DB and filesystem run outputs,
then measures prediction accuracy, readiness calibration,
similarity usefulness, evidence quality, trust score validity,
knowledge graph fidelity, and cross-system consistency.

Outputs: docs/audit/intelligence_accuracy_audit_v1.md
"""

import json
import math
import os
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs" / "audit"
OUTPUTS_DIR = ROOT / "outputs" / "runs"

sys.path.insert(0, str(ROOT))
from gli_flow.database.migrations import _get_db_path


# ── Helpers ──────────────────────────────────────────────────────────────

def db_conn():
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def load_json(path):
    try:
        return json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


# ── 1. Extract real run outcomes from filesystem ────────────────────────

def extract_run_outcomes():
    """Read actual outcomes from run output directories and DB."""
    outcomes = {}
    conn = db_conn()
    db_runs_map = {}
    for r in get_db_runs(conn):
        db_runs_map[r["run_id"]] = r

    if not OUTPUTS_DIR.exists():
        return outcomes
    for run_dir in sorted(OUTPUTS_DIR.iterdir()):
        if not run_dir.is_dir():
            continue
        run_id = run_dir.name

        db_info = db_runs_map.get(run_id, {})
        db_status = db_info.get("status", "")
        db_drc_clean = db_info.get("drc_is_clean", 0)
        db_tapeout_ready = db_info.get("tapeout_ready", 0)
        db_lvs_result = db_info.get("lvs_result", "")

        metrics_csv = run_dir / "reports" / "metrics.csv"
        drc_json = run_dir / "reports" / "drc_combined.json"
        lvs_report = run_dir / "reports" / "lvs_report.txt"
        timing_rpt = run_dir / "reports" / "timing.rpt"
        telemetry_dir = run_dir / "telemetry"

        metrics = {}
        if metrics_csv.exists():
            for line in metrics_csv.read_text().strip().splitlines():
                if "," in line:
                    k, v = line.split(",", 1)
                    try:
                        metrics[k.strip()] = float(v.strip())
                    except ValueError:
                        metrics[k.strip()] = v.strip()

        drc_clean = None
        drc_count = None
        if drc_json.exists():
            drc_data = load_json(drc_json)
            if drc_data:
                drc_clean = drc_data.get("drc_clean", drc_data.get("drc_status") == "PASS")
                drc_count = drc_data.get("total_violations", 0)

        lvs_clean = None
        if lvs_report.exists():
            content = lvs_report.read_text().lower()
            lvs_clean = (
                "success" in content
                or "passed" in content
                or ("merged" in content and "subcircuit summary" in content)
            )
        signoff_setup_rpt = run_dir / "reports" / "signoff_setup.rpt"
        if not lvs_report.exists() and signoff_setup_rpt.exists():
            lvs_clean = True

        timing_wns = metrics.get("wns")
        timing_tns = metrics.get("tns")

        outcome = {
            "run_id": run_id,
            "wns": timing_wns,
            "tns": timing_tns,
            "utilization": metrics.get("utilization"),
            "cell_count": metrics.get("cell_count"),
            "runtime_sec": metrics.get("runtime_sec"),
            "drc_clean": drc_clean if drc_clean is not None else (db_drc_clean == 1),
            "drc_count": drc_count,
            "lvs_clean": lvs_clean if lvs_clean is not None else (db_lvs_result.lower() in ("success", "clean", "passed") if db_lvs_result else None),
            "db_status": db_status,
            "db_tapeout_ready": db_tapeout_ready,
        }

        sta_files = list(run_dir.glob("reports/*sta*")) + list(run_dir.glob("reports/*timing*")) + list(run_dir.glob("reports/signoff_setup*"))
        outcome["timing_met"] = None
        if outcome.get("wns") is not None and outcome["wns"] >= 0:
            outcome["timing_met"] = True
        elif outcome.get("wns") is not None and outcome["wns"] < 0:
            outcome["timing_met"] = False
        for sta_f in sta_files:
            content = sta_f.read_text().lower()
            if "all paths met" in content:
                outcome["timing_met"] = True
            if "timing violation" in content or "failing" in content:
                outcome["timing_met"] = False

        outcomes[run_id] = outcome
    return outcomes


# ── 2. Extract DB state ─────────────────────────────────────────────────

def get_db_runs(conn):
    cursor = conn.execute("SELECT * FROM runs ORDER BY timestamp")
    return [dict(r) for r in cursor.fetchall()]


def get_db_failure_entries(conn):
    cursor = conn.execute("SELECT * FROM failure_atlas_entries ORDER BY detected_at")
    return [dict(r) for r in cursor.fetchall()]


def get_db_resolution_patterns(conn):
    try:
        cursor = conn.execute("SELECT * FROM resolution_patterns ORDER BY last_seen")
        return [dict(r) for r in cursor.fetchall()]
    except (sqlite3.OperationalError, sqlite3.DatabaseError):
        return []


def get_db_execution_intelligence(conn):
    try:
        cursor = conn.execute("SELECT * FROM execution_intelligence ORDER BY timestamp")
        return [dict(r) for r in cursor.fetchall()]
    except (sqlite3.OperationalError, sqlite3.DatabaseError):
        return []


# ── 3. Audit: Prediction Accuracy ──────────────────────────────────────

def audit_prediction_accuracy(conn, run_outcomes):
    """Compare predicted risks against actual run outcomes.

    For each run with telemetry data, simulate what the prediction engines
    would have predicted and compare against whether the run actually succeeded/failed.
    """
    from intelligence.failure_risk_engine import FailureRiskEngine
    from intelligence.prediction_models import ReadinessPredictor, ConvergencePredictor
    from intelligence.prediction_analysis import SimilarityEngine, ConfidenceEngine

    engine = FailureRiskEngine()
    readiness = ReadinessPredictor()
    convergence = ConvergencePredictor()
    similarity = SimilarityEngine()
    confidence = ConfidenceEngine()

    results = []
    for run_id, outcome in run_outcomes.items():
        if outcome["wns"] is None:
            continue
        features = {
            "wns": outcome["wns"] if outcome["wns"] is not None else 0.0,
            "tns": outcome["tns"] if outcome["tns"] is not None else 0.0,
            "utilization": outcome["utilization"] if outcome["utilization"] is not None else 50.0,
            "drc_violations": outcome["drc_count"] if outcome["drc_count"] is not None else 0,
            "stage": "signoff",
        }

        similar = similarity.find_similar(features)
        risk = engine.predict_full_risk(features)
        read_score = readiness.predict_readiness(features)
        conv_score = convergence.predict_convergence(features)
        conf_score = confidence.measure_confidence(risk)

        actual_success = (
            outcome.get("drc_clean") is not False
            and outcome.get("lvs_clean") is not False
            and outcome.get("timing_met") is not False
        )
        if outcome.get("drc_clean") is None and outcome.get("lvs_clean") is None:
            if outcome.get("db_status") == "SUCCESS":
                actual_success = True
            else:
                actual_success = None

        results.append({
            "run_id": run_id,
            "features": features,
            "similar_count": len(similar),
            "risks": risk,
            "readiness": read_score,
            "convergence": conv_score,
            "confidence": conf_score,
            "actual_success": actual_success,
            "actual_drc_clean": outcome.get("drc_clean"),
            "actual_lvs_clean": outcome.get("lvs_clean"),
        })
    return results


def measure_prediction_accuracy(pred_results):
    """Compute accuracy metrics across all prediction types."""
    if not pred_results:
        return {"error": "No prediction results to evaluate"}

    metrics = {
        "total_runs_evaluated": len(pred_results),
        "runs_with_actual_outcomes": sum(1 for r in pred_results if r["actual_success"] is not None),
    }

    avg_risks = Counter()
    for r in pred_results:
        for ftype in ["Timing", "Routing", "DRC", "LVS", "Power"]:
            avg_risks[ftype] += r["risks"].get(ftype, {}).get("risk", 0)
    for ftype in avg_risks:
        avg_risks[ftype] = round(avg_risks[ftype] / len(pred_results), 2)
    metrics["average_predicted_risks"] = dict(avg_risks)

    readiness_scores = [r["readiness"] for r in pred_results]
    metrics["average_predicted_readiness"] = round(sum(readiness_scores) / len(readiness_scores), 4) if readiness_scores else 0.0
    metrics["readiness_range"] = [round(min(readiness_scores), 4), round(max(readiness_scores), 4)] if readiness_scores else [0, 0]

    conv_scores = [r["convergence"] for r in pred_results]
    metrics["average_predicted_convergence"] = round(sum(conv_scores) / len(conv_scores), 4) if conv_scores else 0.0

    conf_scores = [r["confidence"] for r in pred_results]
    metrics["average_confidence"] = round(sum(conf_scores) / len(conf_scores), 4) if conf_scores else 0.0

    conf_vs_actual = [(r["confidence"], r["actual_success"]) for r in pred_results if r["actual_success"] is not None]
    if conf_vs_actual:
        correct = sum(1 for c, a in conf_vs_actual if (c > 0.5) == a)
        metrics["confidence_accuracy"] = round(correct / len(conf_vs_actual), 4)
    else:
        metrics["confidence_accuracy"] = None

    actual_outcomes = [r["actual_success"] for r in pred_results if r["actual_success"] is not None]
    if actual_outcomes:
        metrics["actual_success_rate"] = round(sum(actual_outcomes) / len(actual_outcomes), 4)
        metrics["actual_failure_rate"] = round(1.0 - metrics["actual_success_rate"], 4)
    else:
        metrics["actual_success_rate"] = None
        metrics["actual_failure_rate"] = None

    return metrics


# ── 4. Audit: Readiness Calibration ────────────────────────────────────

def audit_readiness_calibration(pred_results):
    """Compare predicted readiness vs actual outcomes to measure calibration error."""
    from intelligence.readiness_correlation import ReadinessCorrelationEngine
    corr_engine = ReadinessCorrelationEngine()

    calibration_results = []
    for r in pred_results:
        if r["actual_success"] is None:
            continue
        telemetry = r["features"]
        readiness_data = {"TapeoutReady": r["readiness"] * 100, "Implementation": 50, "Signoff": 50}
        correlation = corr_engine.correlate(telemetry, readiness_data)

        error = abs(r["readiness"] - (1.0 if r["actual_success"] else 0.0))
        calibration_results.append({
            "run_id": r["run_id"],
            "predicted_readiness": r["readiness"],
            "actual_outcome": r["actual_success"],
            "calibration_error": error,
            "evidence_based_adjustment": correlation.get("evidence_based_adjustment", 0),
            "telemetry_gap": correlation.get("telemetry_readiness_gap", 0),
        })

    if not calibration_results:
        return {"error": "No runs with actual outcomes for calibration"}

    errors = [c["calibration_error"] for c in calibration_results]
    mae = sum(errors) / len(errors)
    mse = sum(e ** 2 for e in errors) / len(errors)

    return {
        "total_calibrated": len(calibration_results),
        "mean_absolute_error": round(mae, 4),
        "root_mean_squared_error": round(math.sqrt(mse), 4),
        "max_error": round(max(errors), 4),
        "min_error": round(min(errors), 4),
        "std_error": round(math.sqrt(sum((e - mae) ** 2 for e in errors) / len(errors)), 4),
        "calibration_results": calibration_results,
    }


# ── 5. Audit: Similarity Usefulness ─────────────────────────────────────

def audit_similarity_usefulness(conn, pred_results):
    """Verify that similar runs actually have similar outcomes.

    Measures: for each run, do its similar runs (same failure types, metrics)
    share the same outcome status?
    """
    from failure_atlas.prediction.similarity import ExecutionSimilarityEngine
    sim_engine = ExecutionSimilarityEngine()

    similarity_scores = []
    for r in pred_results:
        similar = sim_engine.find_similar(r["features"])
        if len(similar) < 2:
            continue
        similarities = [s["similarity"] for s in similar]
        run_ids = [s["run_id"] for s in similar]

        same_failure_types = 0
        total_comparisons = 0
        for i, a in enumerate(similar):
            for b in similar[i + 1:]:
                total_comparisons += 1
                if a.get("failure_type") == b.get("failure_type"):
                    same_failure_types += 1

        similarity_scores.append({
            "run_id": r["run_id"],
            "num_similar": len(similar),
            "avg_similarity": round(sum(similarities) / len(similarities), 4),
            "max_similarity": round(max(similarities), 4),
            "min_similarity": round(min(similarities), 4),
            "failure_type_agreement": round(same_failure_types / total_comparisons, 4) if total_comparisons > 0 else 0,
            "similar_run_ids": run_ids,
        })

    if not similarity_scores:
        return {"error": "No similarity comparisons possible"}

    agreements = [s["failure_type_agreement"] for s in similarity_scores]
    avg_sims = [s["avg_similarity"] for s in similarity_scores]

    return {
        "total_runs_with_similarity": len(similarity_scores),
        "avg_similarity_score": round(sum(avg_sims) / len(avg_sims), 4),
        "avg_failure_type_agreement": round(sum(agreements) / len(agreements), 4),
        "similarity_usefulness_score": round(
            (sum(agreements) / len(agreements) * 0.5 + sum(avg_sims) / len(avg_sims) * 0.5),
            4,
        ),
        "details": similarity_scores,
    }


# ── 6. Audit: Recommendation Evidence ──────────────────────────────────

def audit_recommendation_evidence(conn):
    """For every recommendation in the DB, verify historical evidence exists."""
    from intelligence.recommendation_engine import RecommendationEngine
    from intelligence.warehouse import TelemetryWarehouse

    warehouse = TelemetryWarehouse()
    engine = RecommendationEngine(warehouse)

    failure_types = set()
    cursor = conn.execute("SELECT DISTINCT failure_type FROM failure_atlas_entries WHERE failure_type IS NOT NULL")
    for row in cursor.fetchall():
        failure_types.add(row["failure_type"])

    recommendation_audit = []
    for ft in sorted(failure_types):
        rec = engine.get_recommendation(ft)
        recs_by_evidence = engine.get_recommendations_by_evidence(ft)

        has_resolution_pattern = rec.historical_success_rate > 0 or rec.trust_score > 0
        evidence_count = len(recs_by_evidence)
        total_supporting = sum(e.get("sample_size", 0) for e in recs_by_evidence)

        recommendation_audit.append({
            "failure_type": ft,
            "recommended_fix": rec.recommended_fix,
            "historical_success_rate": rec.historical_success_rate,
            "trust_score": rec.trust_score,
            "has_evidence": has_resolution_pattern,
            "evidence_count": evidence_count,
            "total_supporting_runs": total_supporting,
            "evidence_details": recs_by_evidence,
        })

    return {
        "total_recommendation_types": len(recommendation_audit),
        "with_evidence": sum(1 for r in recommendation_audit if r["has_evidence"]),
        "without_evidence": sum(1 for r in recommendation_audit if not r["has_evidence"]),
        "avg_success_rate": round(
            sum(r["historical_success_rate"] for r in recommendation_audit) / len(recommendation_audit), 4
        ) if recommendation_audit else 0.0,
        "avg_trust_score": round(
            sum(r["trust_score"] for r in recommendation_audit) / len(recommendation_audit), 4
        ) if recommendation_audit else 0.0,
        "details": recommendation_audit,
    }


# ── 7. Audit: Trust Score Validity ──────────────────────────────────────

def audit_trust_scores(conn):
    """Verify HIGH trust recommendations outperform LOW trust ones."""
    rows = get_db_resolution_patterns(conn)
    if not rows:
        return {"error": "No resolution patterns to evaluate"}

    by_level = {"HIGH": [], "MEDIUM": [], "LOW": []}
    for r in rows:
        level = r.get("trust_level", "LOW")
        if level in by_level:
            by_level[level].append(r)

    trust_audit = {}
    for level, patterns in by_level.items():
        if not patterns:
            trust_audit[level] = {"count": 0, "avg_success_rate": None, "avg_confidence": None}
            continue
        success_rates = []
        confidences = []
        for p in patterns:
            total = p.get("success_count", 0) + p.get("failure_count", 0)
            sr = p.get("success_count", 0) / total if total > 0 else 0
            success_rates.append(sr)
            confidences.append(p.get("confidence", 0))
        trust_audit[level] = {
            "count": len(patterns),
            "avg_success_rate": round(sum(success_rates) / len(success_rates), 4),
            "avg_confidence": round(sum(confidences) / len(confidences), 4),
        }

    if trust_audit.get("HIGH") and trust_audit.get("LOW"):
        high_sr = trust_audit["HIGH"]["avg_success_rate"]
        low_sr = trust_audit["LOW"]["avg_success_rate"]
        trust_audit["high_outperforms_low"] = high_sr > low_sr if high_sr is not None and low_sr is not None else None
        trust_audit["performance_delta"] = round((high_sr or 0) - (low_sr or 0), 4)
    else:
        trust_audit["high_outperforms_low"] = None
        trust_audit["performance_delta"] = None

    return trust_audit


# ── 8. Audit: Knowledge Graph Fidelity ──────────────────────────────────

def audit_knowledge_graph(conn):
    """Verify knowledge graph relationships reflect actual stored records."""
    from intelligence.knowledge_graph import KnowledgeGraphBuilder
    builder = KnowledgeGraphBuilder()
    graph = builder.build_from_warehouse()

    entries = get_db_failure_entries(conn)
    entry_ids = {e["id"] for e in entries}
    entry_failure_ids = {e.get("failure_id") for e in entries if e.get("failure_id")}

    graph_entity_ids = {e["id"] for e in graph["entities"] if e["type"] == "Failure"}
    graph_failure_ids = {e["id"] for e in graph["entities"] if e["type"] == "Failure"}

    synthetic_entities = graph_entity_ids - (entry_ids | entry_failure_ids)
    synthetic_relationships = 0
    for rel in graph["relationships"]:
        if rel["from"] not in entry_ids and rel["from"] not in entry_failure_ids:
            synthetic_relationships += 1

    return {
        "total_db_entries": len(entries),
        "total_graph_entities": len(graph["entities"]),
        "total_graph_relationships": len(graph["relationships"]),
        "db_entries_matched_in_graph": len(graph_failure_ids & (entry_ids | entry_failure_ids)),
        "synthetic_entities": len(synthetic_entities),
        "synthetic_relationships": synthetic_relationships,
        "relationship_types": dict(Counter(r["type"] for r in graph["relationships"])),
        "entity_types": dict(Counter(e["type"] for e in graph["entities"])),
        "graph_clean": len(synthetic_entities) == 0 and synthetic_relationships == 0,
    }


# ── 9. Audit: Failure Atlas Signature Mapping ───────────────────────────

def audit_failure_atlas_mapping(conn, pred_results):
    """Verify predictions and recommendations map to real signatures."""
    entries = get_db_failure_entries(conn)
    signatures_in_db = set()
    for e in entries:
        sig = e.get("signature")
        if sig:
            signatures_in_db.add(sig)

    run_ids_with_entries = set()
    for e in entries:
        run_id = e.get("run_id")
        if run_id:
            run_ids_with_entries.add(run_id)

    predicted_run_ids = set(r["run_id"] for r in pred_results)
    overlapping = predicted_run_ids & run_ids_with_entries

    from intelligence.recommendation_engine import RecommendationEngine
    from intelligence.warehouse import TelemetryWarehouse
    engine = RecommendationEngine(TelemetryWarehouse())

    failure_types_in_db = set()
    for e in entries:
        ft = e.get("failure_type")
        if ft:
            failure_types_in_db.add(ft)

    recs_mapped = 0
    for ft in failure_types_in_db:
        rec = engine.get_recommendation(ft)
        if rec.recommended_fix != "Manual Review":
            recs_mapped += 1

    return {
        "total_db_entries": len(entries),
        "unique_signatures": len(signatures_in_db),
        "runs_with_entries": len(run_ids_with_entries),
        "runs_with_predictions_overlapping_entries": len(overlapping),
        "overlapping_run_ids": list(overlapping),
        "failure_types_in_db": len(failure_types_in_db),
        "recommendations_mapped_to_signatures": recs_mapped,
        "signature_coverage": round(len(signatures_in_db) / max(len(entries), 1), 4),
    }


# ── 10. Audit: Warehouse Consistency ────────────────────────────────────

def audit_warehouse_consistency(conn):
    """Verify Warehouse, Repository, Knowledge Graph, and Prediction Engine agree."""
    from intelligence.warehouse import TelemetryWarehouse
    warehouse = TelemetryWarehouse()

    db_run_count = len(get_db_runs(conn))
    db_entry_count = len(get_db_failure_entries(conn))

    warehouse_exec_count = warehouse.count_records()
    warehouse_failures = warehouse.get_all_failures()

    from failure_atlas.repository import FailureAtlasRepository
    repo = FailureAtlasRepository()
    repo_total = repo.count_entries()
    repo_fixed = repo.get_statistics().get("fixed_entries", 0)

    agreement = {
        "db_total_entries": db_entry_count,
        "warehouse_execution_records": warehouse_exec_count,
        "repository_count_entries": repo_total,
        "entries_agree": db_entry_count == repo_total,
        "db_run_count": db_run_count,
        "warehouse_failure_types": len(warehouse_failures),
        "repository_fixed_count": repo_fixed,
        "warehouse_vs_repository": "CONSISTENT" if db_entry_count == repo_total else "INCONSISTENT",
    }

    return agreement


# ── 11. Audit: False Confidence & Edge Cases ────────────────────────────

def audit_false_confidence(pred_results, calibration):
    """Identify high-confidence predictions that were wrong."""
    false_positives = []
    false_negatives = []

    for r in pred_results:
        if r["actual_success"] is None:
            continue
        high_conf = r["confidence"] > 0.7
        predicted_success = r["readiness"] > 0.5

        if high_conf and predicted_success and not r["actual_success"]:
            false_positives.append({
                "run_id": r["run_id"],
                "confidence": r["confidence"],
                "predicted_readiness": r["readiness"],
                "risks": r["risks"],
            })
        elif high_conf and not predicted_success and r["actual_success"]:
            false_negatives.append({
                "run_id": r["run_id"],
                "confidence": r["confidence"],
                "predicted_readiness": r["readiness"],
                "risks": r["risks"],
            })

    return {
        "false_positives": len(false_positives),
        "false_negatives": len(false_negatives),
        "false_positive_details": false_positives,
        "false_negative_details": false_negatives,
    }


def audit_edge_cases(conn):
    """Evaluate sparse data, single-occurrence failures, rare signatures."""
    entries = get_db_failure_entries(conn)

    failure_type_counts = Counter(e.get("failure_type", "UNKNOWN") for e in entries)
    single_occurrence = [ft for ft, c in failure_type_counts.items() if c == 1]
    rare = [ft for ft, c in failure_type_counts.items() if c <= 3]

    rows = get_db_resolution_patterns(conn)
    low_sample_patterns = [r for r in rows if (r.get("success_count", 0) + r.get("failure_count", 0)) < 5]

    return {
        "total_failure_types": len(failure_type_counts),
        "single_occurrence_types": len(single_occurrence),
        "single_occurrence_list": single_occurrence,
        "rare_types": len(rare),
        "rare_list": rare,
        "failure_type_distribution": dict(failure_type_counts.most_common()),
        "low_sample_patterns": len(low_sample_patterns),
        "low_sample_details": [
            {
                "fingerprint": p.get("failure_fingerprint", ""),
                "total_attempts": p.get("success_count", 0) + p.get("failure_count", 0),
                "confidence": p.get("confidence", 0),
            }
            for p in low_sample_patterns[:20]
        ],
    }


# ── 12. Trustworthiness Score ───────────────────────────────────────────

def compute_trustworthiness_score(pred_accuracy, calibration, similarity, recommendation,
                                   trust_audit, kg_audit, atlas_audit, consistency,
                                   false_confidence, edge_cases):
    """Compute a single Trustworthiness Score from all audit dimensions."""

    def safe_score(val, default=0.0):
        return val if val is not None and not isinstance(val, str) else default

    # Accuracy (0-1)
    accuracy_score = safe_score(pred_accuracy.get("confidence_accuracy"), 0.5) if isinstance(pred_accuracy, dict) else 0.5

    # Calibration (0-1): inverse of MAE
    cal_error = safe_score(calibration.get("mean_absolute_error", 0.5) if isinstance(calibration, dict) else 0.5, 0.5)
    calibration_score = max(0.0, 1.0 - cal_error)

    # Evidence Quality (0-1)
    rec_evidence_ratio = 0.0
    if isinstance(recommendation, dict):
        total = recommendation.get("total_recommendation_types", 0)
        if total > 0:
            rec_evidence_ratio = recommendation.get("with_evidence", 0) / total
    evidence_score = rec_evidence_ratio

    # Consistency (0-1)
    consistency_score = 1.0 if isinstance(consistency, dict) and consistency.get("entries_agree") else 0.5

    # False confidence penalty
    fp_score = 0.0
    if isinstance(false_confidence, dict):
        fp = false_confidence.get("false_positives", 0)
        fn = false_confidence.get("false_negatives", 0)
        total_bad = fp + fn
        total_preds = pred_accuracy.get("total_runs_evaluated", 0) if isinstance(pred_accuracy, dict) else 0
        fp_penalty = min(1.0, total_bad / max(total_preds, 1))
        fp_score = 1.0 - fp_penalty

    # Similarity usefulness
    sim_score = 0.5
    if isinstance(similarity, dict) and "similarity_usefulness_score" in similarity:
        sim_score = safe_score(similarity["similarity_usefulness_score"], 0.5)

    # Knowledge graph fidelity
    kg_score = 1.0 if isinstance(kg_audit, dict) and kg_audit.get("graph_clean") else 0.5

    # Edge case robustness
    edge_penalty = 0.0
    if isinstance(edge_cases, dict):
        single = edge_cases.get("single_occurrence_types", 0)
        low_sample = edge_cases.get("low_sample_patterns", 0)
        edge_penalty = min(0.3, (single * 0.02 + low_sample * 0.02))

    # Weighted combination
    trustworthiness = (
        accuracy_score * 0.25
        + calibration_score * 0.15
        + evidence_score * 0.15
        + consistency_score * 0.10
        + fp_score * 0.10
        + sim_score * 0.10
        + kg_score * 0.10
        + (1.0 - edge_penalty) * 0.05
    )

    return {
        "trustworthiness_score": round(trustworthiness, 4),
        "component_scores": {
            "accuracy": round(accuracy_score, 4),
            "calibration": round(calibration_score, 4),
            "evidence_quality": round(evidence_score, 4),
            "consistency": round(consistency_score, 4),
            "false_confidence_penalty": round(fp_score, 4),
            "similarity_usefulness": round(sim_score, 4),
            "knowledge_graph_fidelity": round(kg_score, 4),
            "edge_case_robustness": round(1.0 - edge_penalty, 4),
        },
        "weights": {
            "accuracy": 0.25,
            "calibration": 0.15,
            "evidence_quality": 0.15,
            "consistency": 0.10,
            "false_confidence_penalty": 0.10,
            "similarity_usefulness": 0.10,
            "knowledge_graph_fidelity": 0.10,
            "edge_case_robustness": 0.05,
        },
    }


# ── Generate Report ─────────────────────────────────────────────────────

def generate_report(
    run_outcomes, pred_results, pred_accuracy, calibration, similarity,
    recommendation, trust_audit, kg_audit, atlas_audit, consistency,
    false_confidence, edge_cases, trustworthiness,
):
    report = []
    def w(s): report.append(s)
    def h1(s): w(f"\n# {s}\n")
    def h2(s): w(f"\n## {s}\n")
    def h3(s): w(f"\n### {s}\n")
    def code(s): w(f"  {s}")
    def table(headers, rows):
        header = "| " + " | ".join(headers) + " |"
        sep = "| " + " | ".join("---" for _ in headers) + " |"
        w(header)
        w(sep)
        for row in rows:
            w("| " + " | ".join(str(c) for c in row) + " |")
        w("")

    h1("Intelligence Accuracy & Trustworthiness Audit v1")
    w(f"\n**Generated**: {datetime.now(timezone.utc).isoformat()}")
    w(f"\n**Data Source**: `~/.gli_flow/gli_flow.db` + `outputs/runs/`")

    # ── Section 1: Data Inventory ──
    h1("1. Data Inventory")
    w(f"\n**Total DB runs**: {len(get_db_runs(db_conn()))}")
    w(f"**DB failure atlas entries**: {len(get_db_failure_entries(db_conn()))}")
    w(f"**Run output directories**: {len(run_outcomes)}")
    w(f"**Runs with measurable metrics**: {len(pred_results)}")
    w(f"**Runs with actual outcomes**: {sum(1 for r in run_outcomes.values() if r.get('wns') is not None)}")

    # ── Section 2: Prediction Accuracy ──
    h1("2. Prediction Accuracy Audit")
    if isinstance(pred_accuracy, dict) and "error" not in pred_accuracy:
        h2("2.1 Aggregate Metrics")
        table(
            ["Metric", "Value"],
            [
                ["Total runs evaluated", pred_accuracy.get("total_runs_evaluated", 0)],
                ["Runs with actual outcomes", pred_accuracy.get("runs_with_actual_outcomes", 0)],
                ["Average predicted readiness", pred_accuracy.get("average_predicted_readiness", 0)],
                ["Readiness range", str(pred_accuracy.get("readiness_range", [0, 0]))],
                ["Average predicted convergence", pred_accuracy.get("average_predicted_convergence", 0)],
                ["Average prediction confidence", pred_accuracy.get("average_confidence", 0)],
                ["Confidence accuracy", pred_accuracy.get("confidence_accuracy", "N/A")],
                ["Actual success rate", pred_accuracy.get("actual_success_rate", "N/A")],
                ["Actual failure rate", pred_accuracy.get("actual_failure_rate", "N/A")],
            ],
        )

        h2("2.2 Average Predicted Risks by Failure Type")
        risks = pred_accuracy.get("average_predicted_risks", {})
        table(["Failure Type", "Average Predicted Risk (%)"], [[ft, risks[ft]] for ft in sorted(risks)])

        h2("2.3 Per-Run Prediction Details")
        table(
            ["Run ID", "Readiness", "Confidence", "Timing Risk", "DRC Risk", "Actual Success"],
            [
                [
                    r["run_id"][:30],
                    r["readiness"],
                    r["confidence"],
                    r["risks"].get("Timing", {}).get("risk", 0),
                    r["risks"].get("DRC", {}).get("risk", 0),
                    r["actual_success"],
                ]
                for r in pred_results[:25]
            ],
        )
    else:
        w(f"\n⚠ No prediction results available: {pred_accuracy.get('error', 'unknown')}")

    # ── Section 3: Readiness Calibration ──
    h1("3. Readiness Calibration Audit")
    if isinstance(calibration, dict) and "error" not in calibration:
        table(
            ["Metric", "Value"],
            [
                ["Total calibrated runs", calibration.get("total_calibrated", 0)],
                ["Mean Absolute Error (MAE)", calibration.get("mean_absolute_error", 0)],
                ["Root Mean Squared Error (RMSE)", calibration.get("root_mean_squared_error", 0)],
                ["Max Error", calibration.get("max_error", 0)],
                ["Min Error", calibration.get("min_error", 0)],
                ["Std Error", calibration.get("std_error", 0)],
            ],
        )

        h3("Per-Run Calibration Details")
        table(
            ["Run ID", "Predicted", "Actual", "Error"],
            [
                [c["run_id"][:30], round(c["predicted_readiness"], 4), c["actual_outcome"], round(c["calibration_error"], 4)]
                for c in calibration.get("calibration_results", [])
            ],
        )
    else:
        w(f"\n⚠ No calibration results: {calibration.get('error', 'unknown')}")

    # ── Section 4: Similarity Usefulness ──
    h1("4. Similarity Usefulness Audit")
    if isinstance(similarity, dict) and "error" not in similarity:
        table(
            ["Metric", "Value"],
            [
                ["Runs with similarity comparisons", similarity.get("total_runs_with_similarity", 0)],
                ["Average similarity score", similarity.get("avg_similarity_score", 0)],
                ["Failure type agreement among similars", similarity.get("avg_failure_type_agreement", 0)],
                ["Similarity Usefulness Score", similarity.get("similarity_usefulness_score", 0)],
            ],
        )
    else:
        w(f"\n⚠ {similarity.get('error', 'No similarity data')}")

    # ── Section 5: Recommendation Evidence ──
    h1("5. Recommendation Evidence Audit")
    if isinstance(recommendation, dict) and "error" not in recommendation:
        table(
            ["Metric", "Value"],
            [
                ["Total recommendation types", recommendation.get("total_recommendation_types", 0)],
                ["With evidence", recommendation.get("with_evidence", 0)],
                ["Without evidence", recommendation.get("without_evidence", 0)],
                ["Average historical success rate", recommendation.get("avg_success_rate", 0)],
                ["Average trust score", recommendation.get("avg_trust_score", 0)],
            ],
        )

        h3("Per-Failure-Type Recommendation Evidence")
        table(
            ["Failure Type", "Recommended Fix", "Success Rate", "Trust Score", "Evidence", "Supporting Runs"],
            [
                [
                    d.get("failure_type", ""),
                    d.get("recommended_fix", "")[:20],
                    d.get("historical_success_rate", 0),
                    d.get("trust_score", 0),
                    "YES" if d.get("has_evidence") else "NO",
                    d.get("total_supporting_runs", 0),
                ]
                for d in recommendation.get("details", [])
            ],
        )
    else:
        w(f"\n⚠ {recommendation.get('error', 'No recommendation data')}")

    # ── Section 6: Trust Score Validity ──
    h1("6. Trust Score Audit")
    if isinstance(trust_audit, dict) and "error" not in trust_audit:
        table(
            ["Trust Level", "Count", "Avg Success Rate", "Avg Confidence"],
            [
                [
                    level,
                    data.get("count", 0),
                    data.get("avg_success_rate", "N/A"),
                    data.get("avg_confidence", "N/A"),
                ]
                for level, data in trust_audit.items()
                if isinstance(data, dict) and "count" in data
            ],
        )
        high_outperforms = trust_audit.get("high_outperforms_low")
        delta = trust_audit.get("performance_delta")
        w(f"\n**HIGH outperforms LOW**: {high_outperforms}")
        if delta is not None:
            w(f"**Performance delta**: {delta}")
    else:
        w(f"\n⚠ {trust_audit.get('error', 'No trust score data')}")

    # ── Section 7: Knowledge Graph ──
    h1("7. Knowledge Graph Fidelity Audit")
    if isinstance(kg_audit, dict):
        table(
            ["Metric", "Value"],
            [
                ["Total DB entries", kg_audit.get("total_db_entries", 0)],
                ["Total graph entities", kg_audit.get("total_graph_entities", 0)],
                ["Total graph relationships", kg_audit.get("total_graph_relationships", 0)],
                ["DB entries matched in graph", kg_audit.get("db_entries_matched_in_graph", 0)],
                ["Synthetic entities (no DB match)", kg_audit.get("synthetic_entities", 0)],
                ["Synthetic relationships", kg_audit.get("synthetic_relationships", 0)],
                ["Graph clean (no synthetic links)", kg_audit.get("graph_clean", False)],
            ],
        )
        w(f"\n**Relationship types**: {kg_audit.get('relationship_types', {})}")
        w(f"\n**Entity types**: {kg_audit.get('entity_types', {})}")
    else:
        w("\n⚠ No knowledge graph data")

    # ── Section 8: Failure Atlas Mapping ──
    h1("8. Failure Atlas Signature Mapping Audit")
    if isinstance(atlas_audit, dict):
        table(
            ["Metric", "Value"],
            [
                ["Total DB entries", atlas_audit.get("total_db_entries", 0)],
                ["Unique signatures", atlas_audit.get("unique_signatures", 0)],
                ["Runs with atlas entries", atlas_audit.get("runs_with_entries", 0)],
                ["Runs with predictions + entries", atlas_audit.get("runs_with_predictions_overlapping_entries", 0)],
                ["Failure types in DB", atlas_audit.get("failure_types_in_db", 0)],
                ["Recommendations mapped to signatures", atlas_audit.get("recommendations_mapped_to_signatures", 0)],
                ["Signature coverage ratio", atlas_audit.get("signature_coverage", 0)],
            ],
        )
    else:
        w("\n⚠ No atlas data")

    # ── Section 9: Warehouse Consistency ──
    h1("9. Warehouse Consistency Audit")
    if isinstance(consistency, dict):
        table(
            ["Component", "Records"],
            [
                ["DB failure_atlas_entries table", consistency.get("db_total_entries", 0)],
                ["Warehouse execution records", consistency.get("warehouse_execution_records", 0)],
                ["Repository count entries()", consistency.get("repository_count_entries", 0)],
                ["DB runs table", consistency.get("db_run_count", 0)],
                ["Warehouse failure types", consistency.get("warehouse_failure_types", 0)],
                ["Repository fixed entries", consistency.get("repository_fixed_count", 0)],
            ],
        )
        w(f"\n**Consensus**: {consistency.get('warehouse_vs_repository', 'UNKNOWN')}")
    else:
        w("\n⚠ No consistency data")

    # ── Section 10: False Confidence ──
    h1("10. False Confidence Audit")
    if isinstance(false_confidence, dict):
        table(
            ["Type", "Count"],
            [
                ["False positives (high confidence but wrong)", false_confidence.get("false_positives", 0)],
                ["False negatives (low confidence but right)", false_confidence.get("false_negatives", 0)],
            ],
        )
        if false_confidence.get("false_positive_details"):
            h3("False Positive Details")
            for fp in false_confidence["false_positive_details"][:10]:
                code(f"- {fp['run_id'][:30]}: confidence={fp['confidence']}, readiness={fp['predicted_readiness']}")
    else:
        w("\n⚠ No false confidence data")

    # ── Section 11: Edge Cases ──
    h1("11. Edge Case Audit")
    if isinstance(edge_cases, dict):
        table(
            ["Metric", "Value"],
            [
                ["Total failure types", edge_cases.get("total_failure_types", 0)],
                ["Single-occurrence types", edge_cases.get("single_occurrence_types", 0)],
                ["Rare types (≤3 occurrences)", edge_cases.get("rare_types", 0)],
                ["Low-sample resolution patterns (<5 attempts)", edge_cases.get("low_sample_patterns", 0)],
            ],
        )
        if edge_cases.get("single_occurrence_list"):
            h3("Single-Occurrence Failure Types")
            for ft in edge_cases["single_occurrence_list"]:
                code(f"- {ft}")
        if edge_cases.get("failure_type_distribution"):
            h3("Failure Type Distribution")
            table(
                ["Failure Type", "Occurrences"],
                [[ft, c] for ft, c in edge_cases["failure_type_distribution"].items()],
            )
    else:
        w("\n⚠ No edge case data")

    # ── Section 12: Trustworthiness Score ──
    h1("12. Trustworthiness Score")
    if isinstance(trustworthiness, dict):
        w(f"\n**Overall Trustworthiness Score**: **{trustworthiness.get('trustworthiness_score', 0) * 100:.1f}%**")
        w("\n### Component Breakdown\n")
        components = trustworthiness.get("component_scores", {})
        weights = trustworthiness.get("weights", {})
        table(
            ["Component", "Score", "Weight", "Weighted Contribution"],
            [
                [
                    comp,
                    f"{score * 100:.1f}%",
                    f"{weights.get(comp, 0) * 100:.0f}%",
                    f"{score * weights.get(comp, 0) * 100:.1f}%",
                ]
                for comp, score in components.items()
            ],
        )

        trust_pct = trustworthiness.get("trustworthiness_score", 0) * 100
        if trust_pct >= 80:
            rating = "PRODUCTION_READY"
            desc = "Intelligence outputs are empirically correct and trustworthy."
        elif trust_pct >= 60:
            rating = "FUNCTIONAL"
            desc = "Intelligence is mostly correct but has known gaps."
        elif trust_pct >= 40:
            rating = "PARTIAL"
            desc = "Intelligence has significant accuracy issues."
        else:
            rating = "STUB"
            desc = "Intelligence cannot be trusted."

        w(f"\n**Rating**: {rating}")
        w(f"\n**Assessment**: {desc}")

    # ── Section 13: Success Criteria ──
    h1("13. Success Criteria Verification")
    w("\n**Target**: GLI can demonstrate that its intelligence outputs are not only data-driven but also empirically correct.\n")
    if isinstance(trustworthiness, dict):
        trust_pct = trustworthiness.get("trustworthiness_score", 0) * 100
        passes = trust_pct >= 70
        w(f"{'✅' if passes else '❌'} Trustworthiness Score: {trust_pct:.1f}% {'≥' if passes else '<'} 70% threshold")
    if isinstance(pred_accuracy, dict):
        ca = pred_accuracy.get("confidence_accuracy")
        if ca is not None:
            passes2 = ca >= 0.6
            w(f"{'✅' if passes2 else '❌'} Prediction confidence accuracy: {ca:.1%} {'≥' if passes2 else '<'} 60%")
    if isinstance(calibration, dict) and "error" not in calibration:
        mae = calibration.get("mean_absolute_error", 1.0)
        passes3 = mae <= 0.4
        w(f"{'✅' if passes3 else '❌'} Calibration error: {mae:.4f} {'≤' if passes3 else '>'} 0.4")
    if isinstance(recommendation, dict):
        ev = recommendation.get("with_evidence", 0)
        tot = recommendation.get("total_recommendation_types", 1)
        passes4 = ev >= tot * 0.5 if tot > 0 else False
        w(f"{'✅' if passes4 else '❌'} Recommendations with evidence: {ev}/{tot} {'≥' if passes4 else '<'} 50%")
    if isinstance(kg_audit, dict):
        passes5 = kg_audit.get("graph_clean", False)
        w(f"{'✅' if passes5 else '❌'} Knowledge graph has no synthetic links: {passes5}")

    return "\n".join(report)


# ── Main ────────────────────────────────────────────────────────────────

def main():
    conn = db_conn()
    print("=== Intelligence Accuracy & Trustworthiness Audit ===\n")

    # Phase 1-2: Extract real data
    print("[1/12] Extracting run outcomes from filesystem...")
    run_outcomes = extract_run_outcomes()
    print(f"  Found {len(run_outcomes)} run directories")

    # Phase 3: Prediction accuracy
    print("[2/12] Measuring prediction accuracy...")
    pred_results = audit_prediction_accuracy(conn, run_outcomes)
    print(f"  Evaluated {len(pred_results)} runs")
    pred_accuracy = measure_prediction_accuracy(pred_results)
    if isinstance(pred_accuracy, dict) and "error" not in pred_accuracy:
        print(f"  Avg readiness: {pred_accuracy.get('average_predicted_readiness')}, "
              f"Avg confidence: {pred_accuracy.get('average_confidence')}")

    # Phase 4: Readiness calibration
    print("[3/12] Measuring readiness calibration...")
    calibration = audit_readiness_calibration(pred_results)
    if isinstance(calibration, dict) and "error" not in calibration:
        print(f"  MAE: {calibration.get('mean_absolute_error')}, "
              f"RMSE: {calibration.get('root_mean_squared_error')}")

    # Phase 5: Similarity usefulness
    print("[4/12] Auditing similarity usefulness...")
    similarity = audit_similarity_usefulness(conn, pred_results)
    if isinstance(similarity, dict) and "error" not in similarity:
        print(f"  Usefulness score: {similarity.get('similarity_usefulness_score')}")

    # Phase 6: Recommendation evidence
    print("[5/12] Auditing recommendation evidence...")
    recommendation = audit_recommendation_evidence(conn)
    if isinstance(recommendation, dict) and "error" not in recommendation:
        print(f"  {recommendation.get('with_evidence')}/{recommendation.get('total_recommendation_types')} "
              f"types with evidence")

    # Phase 7: Trust scores
    print("[6/12] Auditing trust scores...")
    trust_audit = audit_trust_scores(conn)
    if isinstance(trust_audit, dict) and "error" not in trust_audit:
        high = trust_audit.get("HIGH", {})
        low = trust_audit.get("LOW", {})
        print(f"  HIGH trust patterns: {high.get('count', 0)}, "
              f"LOW trust patterns: {low.get('count', 0)}")
        if trust_audit.get("high_outperforms_low") is not None:
            print(f"  HIGH outperforms LOW: {trust_audit['high_outperforms_low']}")

    # Phase 8: Knowledge graph fidelity
    print("[7/12] Auditing knowledge graph...")
    kg_audit = audit_knowledge_graph(conn)
    if isinstance(kg_audit, dict):
        print(f"  {kg_audit.get('total_graph_entities')} entities, "
              f"{kg_audit.get('total_graph_relationships')} relationships, "
              f"clean={kg_audit.get('graph_clean')}")

    # Phase 9: Failure Atlas mapping
    print("[8/12] Auditing failure atlas mapping...")
    atlas_audit = audit_failure_atlas_mapping(conn, pred_results)

    # Phase 10: Warehouse consistency
    print("[9/12] Auditing warehouse consistency...")
    consistency = audit_warehouse_consistency(conn)

    # Phase 11: False confidence
    print("[10/12] Auditing false confidence...")
    false_confidence = audit_false_confidence(pred_results, calibration)
    if isinstance(false_confidence, dict):
        print(f"  False positives: {false_confidence.get('false_positives')}, "
              f"False negatives: {false_confidence.get('false_negatives')}")

    # Phase 12: Edge cases
    print("[11/12] Auditing edge cases...")
    edge_cases = audit_edge_cases(conn)
    if isinstance(edge_cases, dict):
        print(f"  Single-occurrence types: {edge_cases.get('single_occurrence_types')}, "
              f"Low-sample patterns: {edge_cases.get('low_sample_patterns')}")

    # Compute trustworthiness score
    print("[12/12] Computing trustworthiness score...")
    trustworthiness = compute_trustworthiness_score(
        pred_accuracy, calibration, similarity, recommendation,
        trust_audit, kg_audit, atlas_audit, consistency,
        false_confidence, edge_cases,
    )
    print(f"  Overall Trustworthiness: {trustworthiness.get('trustworthiness_score', 0) * 100:.1f}%")

    # Generate report
    print("\nGenerating audit report...")
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    report = generate_report(
        run_outcomes, pred_results, pred_accuracy, calibration, similarity,
        recommendation, trust_audit, kg_audit, atlas_audit, consistency,
        false_confidence, edge_cases, trustworthiness,
    )
    report_path = DOCS_DIR / "intelligence_accuracy_audit_v1.md"
    report_path.write_text(report)
    print(f"\nReport written to: {report_path}")
    print(f"Report length: {len(report)} chars")

    conn.close()


if __name__ == "__main__":
    main()
