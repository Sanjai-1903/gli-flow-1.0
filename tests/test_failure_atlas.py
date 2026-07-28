import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


class TestFailureRepository(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.tmp.name
        self.tmp.close()

    def tearDown(self):
        os.unlink(self.db_path)

    def _make_repo(self):
        from failure_atlas.repository import FailureAtlasRepository
        return FailureAtlasRepository(db_path=self.db_path)

    def test_insert_and_retrieve(self):
        repo = self._make_repo()
        entry = {
            "run_id": "test_run_1",
            "failure_id": "fail_001",
            "failure_type": "SETUP_VIOLATION",
            "severity": "HIGH",
            "title": "Setup timing violated",
            "description": "WNS=-0.45",
            "confidence": 0.92,
            "signature": "WNS: -0.45",
            "domain": "TIMING",
            "category": "SETUP_VIOLATION",
        }
        eid = repo.insert_entry(entry)
        self.assertIsNotNone(eid)

        failures = repo.get_failures_for_run("test_run_1")
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0]["failure_type"], "SETUP_VIOLATION")
        self.assertEqual(failures[0]["severity"], "HIGH")

    def test_insert_log_signature(self):
        repo = self._make_repo()
        entry = {
            "run_id": "test_run_2",
            "failure_id": "fail_002",
            "failure_type": "DRC",
            "severity": "MEDIUM",
            "title": "Log signature: FA-0003",
            "description": "Found 142 DRC violations",
            "confidence": 0.95,
            "signature": "Found 142 DRC violations",
            "domain": "DRC",
            "category": "DRC_SPACING",
        }
        repo.insert_entry(entry)
        all_f = repo.get_all_failures()
        self.assertEqual(len(all_f), 1)

    def test_resolution_update(self):
        repo = self._make_repo()
        entry = {
            "run_id": "test_run_3",
            "failure_id": "fail_003",
            "failure_type": "HOLD_VIOLATION",
            "severity": "TAPEOUT_BLOCKING",
            "title": "Hold violation",
            "domain": "TIMING",
            "category": "HOLD_VIOLATION",
        }
        eid = repo.insert_entry(entry)

        updated = repo.update_resolution(
            failure_id=eid,
            fix_type="pipeline_insertion",
            fix_description="Added pipeline register",
            fix_run_id="test_run_4",
            before_metrics={"wns": -1.2, "tns": -45.3},
            after_metrics={"wns": 0.35, "tns": 0.0},
        )
        self.assertTrue(updated)

        failure = repo.get_failure_by_id(eid)
        self.assertTrue(failure["fix_applied"])
        self.assertEqual(failure["fix_type"], "pipeline_insertion")

    def test_resolution_confidence_high(self):
        repo = self._make_repo()
        eid = repo.insert_entry({
            "run_id": "r1",
            "failure_id": "f1",
            "failure_type": "SETUP_VIOLATION",
            "severity": "HIGH",
            "domain": "TIMING",
            "category": "SETUP_VIOLATION",
        })
        repo.update_resolution(
            failure_id=eid,
            fix_type="retiming",
            fix_description="retimed",
            fix_run_id="r2",
            before_metrics={"wns": -1.0, "tns": -10.0},
            after_metrics={"wns": 0.5, "tns": 0.0},
        )
        failure = repo.get_failure_by_id(eid)
        self.assertEqual(failure["resolution_confidence"], "HIGH")

    def test_resolution_confidence_low(self):
        repo = self._make_repo()
        eid = repo.insert_entry({
            "run_id": "r1",
            "failure_id": "f2",
            "failure_type": "HOLD_VIOLATION",
            "severity": "HIGH",
            "domain": "TIMING",
            "category": "HOLD_VIOLATION",
        })
        repo.update_resolution(
            failure_id=eid,
            fix_type="buffer_insertion",
            fix_description="buffered",
            fix_run_id="r2",
            before_metrics={"wns": 0.0, "tns": 0.0},
            after_metrics={"wns": -0.5, "tns": -5.0},
        )
        failure = repo.get_failure_by_id(eid)
        self.assertEqual(failure["resolution_confidence"], "LOW")

    def test_get_all_failures_pagination(self):
        repo = self._make_repo()
        for i in range(5):
            repo.insert_entry({
                "run_id": f"run_{i}",
                "failure_id": f"f_{i}",
                "failure_type": "SETUP_VIOLATION",
                "severity": "HIGH",
                "domain": "TIMING",
                "category": "SETUP_VIOLATION",
            })
        all_f = repo.get_all_failures(limit=3, offset=0)
        self.assertEqual(len(all_f), 3)
        all_f2 = repo.get_all_failures(limit=3, offset=3)
        self.assertEqual(len(all_f2), 2)

    def test_get_all_failures_filter_severity(self):
        repo = self._make_repo()
        repo.insert_entry({"run_id": "r1", "failure_id": "f1", "failure_type": "A", "severity": "HIGH", "domain": "T", "category": "A"})
        repo.insert_entry({"run_id": "r2", "failure_id": "f2", "failure_type": "B", "severity": "LOW", "domain": "T", "category": "B"})
        all_f = repo.get_all_failures(severity="HIGH")
        self.assertEqual(len(all_f), 1)

    def test_insert_entry_missing_classification_defaults(self):
        repo = self._make_repo()
        entry = {
            "run_id": "r1",
            "failure_id": "f1",
            "failure_type": "A",
            "severity": "HIGH",
            "domain": "T",
            "category": "A",
            # Missing detection_classification
        }
        eid = repo.insert_entry(entry)
        stored = repo.get_entry(eid)
        self.assertEqual(stored.get("detection_classification"), "")

    def test_insert_entry_with_classification(self):
        repo = self._make_repo()
        entry = {
            "run_id": "r1",
            "failure_id": "f1",
            "failure_type": "A",
            "severity": "HIGH",
            "domain": "T",
            "category": "A",
            "detection_classification": "VERIFIED"
        }
        eid = repo.insert_entry(entry)
        failure = repo.get_failure_by_id(eid)
        self.assertEqual(failure["detection_classification"], "VERIFIED")

    def test_get_all_failures_search(self):
        repo = self._make_repo()
        repo.insert_entry({"run_id": "r1", "failure_id": "f1", "failure_type": "SETUP_VIOLATION", "severity": "HIGH", "title": "setup bad", "domain": "T", "category": "S"})
        repo.insert_entry({"run_id": "r2", "failure_id": "f2", "failure_type": "HOLD_VIOLATION", "severity": "HIGH", "title": "hold bad", "domain": "T", "category": "H"})
        all_f = repo.get_all_failures(search="hold")
        self.assertEqual(len(all_f), 1)

    def test_get_failure_count(self):
        repo = self._make_repo()
        for i in range(3):
            repo.insert_entry({"run_id": f"r{i}", "failure_id": f"f{i}", "failure_type": "A", "severity": "HIGH", "domain": "T", "category": "A"})
        self.assertEqual(repo.get_failure_count(), 3)
        self.assertEqual(repo.get_failure_count(severity="LOW"), 0)

    def test_get_analytics_summary(self):
        repo = self._make_repo()
        eid = repo.insert_entry({"run_id": "r1", "failure_id": "f1", "failure_type": "A", "severity": "HIGH", "domain": "T", "category": "A"})
        repo.update_resolution(eid, "fix", "desc", "r2")
        summary = repo.get_analytics_summary()
        self.assertEqual(summary["total_failures"], 1)
        self.assertEqual(summary["fixed_count"], 1)
        self.assertEqual(summary["success_rate"], 100.0)

    def test_get_common_failures(self):
        repo = self._make_repo()
        repo.insert_entry({"run_id": "r1", "failure_id": "f1", "failure_type": "A", "severity": "HIGH", "domain": "T", "category": "A"})
        repo.insert_entry({"run_id": "r2", "failure_id": "f2", "failure_type": "A", "severity": "HIGH", "domain": "T", "category": "A"})
        repo.insert_entry({"run_id": "r3", "failure_id": "f3", "failure_type": "B", "severity": "HIGH", "domain": "T", "category": "B"})
        common = repo.get_common_failures()
        self.assertEqual(len(common), 2)
        self.assertEqual(common[0]["failure_type"], "A")
        self.assertEqual(common[0]["count"], 2)

    def test_get_fix_effectiveness_min_samples(self):
        repo = self._make_repo()
        eid1 = repo.insert_entry({"run_id": "r1", "failure_id": "f1", "failure_type": "A", "severity": "HIGH", "domain": "T", "category": "A"})
        eid2 = repo.insert_entry({"run_id": "r2", "failure_id": "f2", "failure_type": "A", "severity": "HIGH", "domain": "T", "category": "A"})
        repo.update_resolution(eid1, "fix1", "desc", "r3")
        repo.update_resolution(eid2, "fix1", "desc", "r4")

        effectiveness = repo.get_fix_effectiveness(min_samples=2)
        self.assertEqual(len(effectiveness), 1)
        self.assertEqual(effectiveness[0]["sample_size"], 2)

        effectiveness_5 = repo.get_fix_effectiveness(min_samples=5)
        self.assertEqual(len(effectiveness_5), 0)

    def test_get_qor_improvements(self):
        repo = self._make_repo()
        eid = repo.insert_entry({"run_id": "r1", "failure_id": "f1", "failure_type": "A", "severity": "HIGH", "domain": "T", "category": "A"})
        repo.update_resolution(eid, "retiming", "desc", "r2",
                               before_metrics={"wns": -1.0, "tns": -10.0},
                               after_metrics={"wns": 0.5, "tns": 0.0})
        qor = repo.get_qor_improvements()
        self.assertEqual(len(qor), 1)
        self.assertGreater(qor[0]["avg_wns_improvement"], 0)

    def test_get_failure_trends(self):
        repo = self._make_repo()
        repo.insert_entry({"run_id": "r1", "failure_id": "f1", "failure_type": "A", "severity": "HIGH", "domain": "T", "category": "A", "detected_at": "2025-01-01"})
        repo.insert_entry({"run_id": "r2", "failure_id": "f2", "failure_type": "B", "severity": "HIGH", "domain": "T", "category": "B", "detected_at": "2025-01-01"})
        trends = repo.get_failure_trends()
        self.assertIn("failure_distribution", trends)
        self.assertIn("daily_counts", trends)
        self.assertEqual(len(trends["failure_distribution"]), 2)

    def test_get_mttr_by_type(self):
        repo = self._make_repo()
        repo.insert_entry({"run_id": "r1", "failure_id": "f1", "failure_type": "A", "severity": "HIGH", "domain": "T", "category": "A"})
        mttr = repo.get_mttr_by_type()
        self.assertEqual(len(mttr), 1)

    def test_similar_failures(self):
        repo = self._make_repo()
        eid = repo.insert_entry({"run_id": "r1", "failure_id": "f1", "failure_type": "SETUP_VIOLATION", "severity": "HIGH", "domain": "T", "category": "S"})
        repo.update_resolution(eid, "pipeline_insertion", "added pipe", "r2")
        similar = repo.similar_failures("SETUP_VIOLATION")
        self.assertEqual(len(similar), 1)
        self.assertEqual(similar[0]["fix_type"], "pipeline_insertion")

    def test_regression_events(self):
        repo = self._make_repo()
        repo.insert_entry({"run_id": "r1", "failure_id": "f1", "failure_type": "A", "severity": "HIGH", "domain": "T", "category": "A", "detected_at": "2025-01-01"})
        repo.insert_entry({"run_id": "r2", "failure_id": "f2", "failure_type": "A", "severity": "HIGH", "domain": "T", "category": "A", "detected_at": "2025-01-02"})
        regressions = repo.get_regression_events()
        self.assertEqual(len(regressions), 1)

    def test_detect_failures_empty_metrics(self):
        from failure_atlas.detector import detect_failures
        entries = detect_failures("test_run", {})
        self.assertEqual(len(entries), 0)

    def test_detect_failures_setup_violation(self):
        from failure_atlas.detector import detect_failures
        entries = detect_failures("test_run", {"setup_wns_ns": -0.5})
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].level2_category.value, "SETUP_VIOLATION")

    def test_detect_failures_hold_violation(self):
        from failure_atlas.detector import detect_failures
        entries = detect_failures("test_run", {"hold_whs_ns": -0.3})
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].level2_category.value, "HOLD_VIOLATION")

    def test_detect_failures_overflow(self):
        from failure_atlas.detector import detect_failures
        entries = detect_failures("test_run", {"overflow_h": 0.15, "overflow_v": 0.1})
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].level1_domain.value, "CONGESTION")

    def test_detect_failures_drc(self):
        from failure_atlas.detector import detect_failures
        entries = detect_failures("test_run", {"drc_total_violations": 5, "drc_is_clean": False, "drc_by_category": {"SPACING": 3}})
        found = [e for e in entries if e.level1_domain.value == "DRC"]
        self.assertGreaterEqual(len(found), 1)

    def test_detect_failures_combined(self):
        from failure_atlas.detector import detect_failures
        entries = detect_failures("test_run", {
            "setup_wns_ns": -0.5,
            "hold_whs_ns": -0.1,
            "overflow_h": 0.2,
            "drc_total_violations": 10,
            "drc_is_clean": False,
            "drc_by_category": {"SPACING": 5, "WIDTH": 3},
        })
        self.assertGreaterEqual(len(entries), 3)

    def test_signature_engine_load(self):
        from failure_atlas.signature_engine import load_signatures
        sigs = load_signatures()
        self.assertGreaterEqual(len(sigs), 20)

    def test_signature_engine_scan(self):
        from failure_atlas.signature_engine import load_signatures, scan_file
        import tempfile
        sigs = load_signatures()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            f.write("WNS: -0.45  TNS: -12.3\n")
            f.write("Found 142 DRC violations: 96 min spacing\n")
            log_path = f.name
        findings = scan_file(Path(log_path), sigs)
        os.unlink(log_path)
        self.assertGreaterEqual(len(findings), 1)

    def test_fix_chain_linkage(self):
        repo = self._make_repo()
        eid = repo.insert_entry({
            "run_id": "run_100",
            "failure_id": "fail_chain_1",
            "failure_type": "HOLD_VIOLATION",
            "severity": "TAPEOUT_BLOCKING",
            "domain": "TIMING",
            "category": "HOLD_VIOLATION",
        })
        repo.update_resolution(
            failure_id=eid,
            fix_type="retiming",
            fix_description="Retimed critical path",
            fix_run_id="run_101",
            before_metrics={"wns": -0.32, "tns": -12.0},
            after_metrics={"wns": 0.08, "tns": 0.0},
        )
        failure = repo.get_failure_by_id(eid)
        self.assertEqual(failure["fix_run_id"], "run_101")
        self.assertEqual(failure["fix_type"], "retiming")
        self.assertEqual(failure["resolution_confidence"], "HIGH")

    def test_parent_run_id(self):
        repo = self._make_repo()
        eid = repo.insert_entry({
            "run_id": "run_200",
            "failure_id": "fail_parent",
            "failure_type": "ROUTING_OVERFLOW",
            "severity": "HIGH",
            "domain": "CONGESTION",
            "category": "GLOBAL_OVERFLOW",
            "parent_run_id": "run_199",
        })
        failure = repo.get_failure_by_id(eid)
        self.assertEqual(failure["parent_run_id"], "run_199")


class TestKnowledgeBase(unittest.TestCase):

    def test_knowledge_base_loads(self):
        kb_path = Path(__file__).resolve().parent.parent / "failure_atlas" / "knowledge_base.json"
        self.assertTrue(kb_path.exists())
        kb = json.loads(kb_path.read_text())
        self.assertGreaterEqual(len(kb), 10)
        for key in ["SETUP_VIOLATION", "HOLD_VIOLATION", "ROUTING_OVERFLOW"]:
            self.assertIn(key, kb)
            self.assertIn("remediation_strategies", kb[key])
            self.assertIn("verification_steps", kb[key])

    def test_qor_playbook_loads(self):
        qp_path = Path(__file__).resolve().parent.parent / "failure_atlas" / "qor_playbook.json"
        self.assertTrue(qp_path.exists())
        qp = json.loads(qp_path.read_text())
        for key in ["TIMING_IMPROVEMENT", "AREA_OPTIMIZATION", "POWER_OPTIMIZATION", "CONGESTION_REDUCTION"]:
            self.assertIn(key, qp)


class TestAPIRoutes(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.tmp.name
        self.tmp.close()
        os.environ["GLI_FLOW_DB_PATH"] = self.db_path
        self._reload_server()

    def tearDown(self):
        os.unlink(self.db_path)
        if "GLI_FLOW_DB_PATH" in os.environ:
            del os.environ["GLI_FLOW_DB_PATH"]

    def _reload_server(self):
        import importlib
        for mod in list(sys.modules.keys()):
            if 'backend.server' in mod or 'failure_atlas' in mod:
                del sys.modules[mod]
        import backend.server
        importlib.reload(backend.server)
        self.app = backend.server.app

    def _seed_data(self):
        from failure_atlas.repository import FailureAtlasRepository
        repo = FailureAtlasRepository(db_path=self.db_path)
        repo.insert_entry({
            "run_id": "test_run_seeded",
            "failure_id": "seed_1",
            "failure_type": "SETUP_VIOLATION",
            "severity": "HIGH",
            "title": "Setup violation detected",
            "domain": "TIMING",
            "category": "SETUP_VIOLATION",
        })

    def _get_client(self):
        from fastapi.testclient import TestClient
        return TestClient(self.app)

    def test_failures_endpoint(self):
        client = self._get_client()
        resp = client.get("/failures")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("results", data)
        self.assertIn("total", data)

    def test_run_failures_endpoint(self):
        self._seed_data()
        self._reload_server()
        client = self._get_client()
        resp = client.get("/runs/test_run_seeded/failures")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreaterEqual(len(data), 1)

    def test_failure_detail_endpoint(self):
        self._seed_data()
        self._reload_server()
        client = self._get_client()
        from failure_atlas.repository import FailureAtlasRepository
        repo = FailureAtlasRepository(db_path=self.db_path)
        failures = repo.get_all_failures()
        if failures:
            fid = failures[0]["id"]
            resp = client.get(f"/failures/{fid}")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("similar_failures", resp.json())

    def test_resolution_endpoint(self):
        self._seed_data()
        self._reload_server()
        client = self._get_client()
        from failure_atlas.repository import FailureAtlasRepository
        repo = FailureAtlasRepository(db_path=self.db_path)
        failures = repo.get_all_failures()
        if failures:
            fid = failures[0]["id"]
            resp = client.post(f"/failures/{fid}/resolution", json={
                "fix_type": "pipeline_insertion",
                "fix_description": "Added pipeline stage",
                "fix_run_id": "fix_run_1",
            })
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json()["status"], "ok")

    def test_analytics_summary_endpoint(self):
        client = self._get_client()
        resp = client.get("/analytics/summary")
        self.assertEqual(resp.status_code, 200)

    def test_analytics_endpoints(self):
        client = self._get_client()
        for ep in ["/analytics/common-failures", "/analytics/fix-effectiveness",
                    "/analytics/qor-improvements", "/analytics/failure-trends",
                    "/analytics/resolution-confidence", "/analytics/mttr"]:
            resp = client.get(ep)
            self.assertEqual(resp.status_code, 200, f"{ep} failed")

    def test_knowledge_endpoints(self):
        client = self._get_client()
        resp = client.get("/knowledge/failures")
        self.assertEqual(resp.status_code, 200)
        resp2 = client.get("/knowledge/failures/SETUP_VIOLATION")
        self.assertEqual(resp2.status_code, 200)
        resp3 = client.get("/knowledge/search?q=setup")
        self.assertEqual(resp3.status_code, 200)
        resp4 = client.get("/knowledge/qor")
        self.assertEqual(resp4.status_code, 200)

    def test_run_diff_endpoint(self):
        client = self._get_client()
        conn = sqlite3.connect(self.db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS runs (run_id TEXT PRIMARY KEY, design_name TEXT, wns REAL, tns REAL, utilization REAL, runtime_sec REAL, cell_count INTEGER, qor_score REAL)")
        conn.execute("INSERT OR IGNORE INTO runs (run_id, design_name, wns, tns, qor_score) VALUES ('run_old', 'test', -0.5, -10.0, 0.6)")
        conn.execute("INSERT OR IGNORE INTO runs (run_id, design_name, wns, tns, qor_score) VALUES ('run_new', 'test', -1.2, -45.0, 0.3)")
        conn.commit()
        conn.close()
        self._reload_server()
        client = self._get_client()
        resp = client.get("/runs/run_new/diff/run_old")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("diffs", data)
        self.assertTrue(data["likely_regression"])

    def test_regressions_endpoint(self):
        client = self._get_client()
        resp = client.get("/regressions")
        self.assertEqual(resp.status_code, 200)

    def test_similar_failures_endpoint(self):
        client = self._get_client()
        resp = client.get("/similar-failures/SETUP_VIOLATION")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("results", data)
        self.assertIn("total", data)

    def test_layout_image_endpoints(self):
        import sqlite3
        import shutil
        from pathlib import Path
        from fastapi.testclient import TestClient
        from gli_flow.testing.layout_images import generate_placeholder_images, LAYOUT_IMAGE_NAMES

        outputs_dir = Path(__file__).resolve().parent.parent / "outputs" / "runs"
        run_id = "img_test_run"
        run_dir = outputs_dir / run_id
        reports_dir = run_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        generate_placeholder_images(str(reports_dir))

        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO runs (run_id, design_name, status, timestamp) VALUES (?, ?, ?, datetime('now'))",
            (run_id, "test_design", "SUCCESS"),
        )
        conn.commit()
        conn.close()

        client = TestClient(self.app)
        images = ["final_all", "final_placement", "final_routing", "final_clocks", "final_ir_drop"]
        for name in images:
            resp = client.get(f"/runs/{run_id}/image/{name}")
            self.assertEqual(resp.status_code, 200, f"{name} returned {resp.status_code}")
            ct = resp.headers.get("content-type", "")
            self.assertTrue(
                ct.startswith("image/"),
                f"{name}: expected image/* MIME, got {ct}",
            )
            self.assertGreater(len(resp.content), 0, f"{name}: empty response")

        shutil.rmtree(run_dir, ignore_errors=True)


class TestLayoutImages(unittest.TestCase):

    def test_svg_fallback_generation(self):
        from gli_flow.testing.layout_images import generate_placeholder_images, LAYOUT_IMAGE_NAMES

        with tempfile.TemporaryDirectory() as td:
            reports = Path(td) / "reports"
            reports.mkdir(parents=True)
            generated = generate_placeholder_images(str(reports))
            self.assertEqual(len(generated), len(LAYOUT_IMAGE_NAMES))
            for g in generated:
                p = Path(g)
                self.assertTrue(p.exists())
                self.assertGreater(p.stat().st_size, 0)
                self.assertEqual(p.suffix, ".svg")

    def test_has_real_images(self):
        from gli_flow.testing.layout_images import has_real_images, LAYOUT_IMAGE_NAMES

        with tempfile.TemporaryDirectory() as td:
            reports = Path(td) / "reports"
            reports.mkdir(parents=True)
            self.assertFalse(has_real_images(str(reports)))

            (reports / "final_all.webp").write_text("fake_webp")
            self.assertTrue(has_real_images(str(reports)))

    def test_generate_skips_existing(self):
        from gli_flow.testing.layout_images import generate_placeholder_images, LAYOUT_IMAGE_NAMES

        with tempfile.TemporaryDirectory() as td:
            reports = Path(td) / "reports"
            reports.mkdir(parents=True)

            generated1 = generate_placeholder_images(str(reports))
            self.assertEqual(len(generated1), len(LAYOUT_IMAGE_NAMES))

            generated2 = generate_placeholder_images(str(reports))
            self.assertEqual(len(generated2), 0)


if __name__ == "__main__":
    unittest.main()
