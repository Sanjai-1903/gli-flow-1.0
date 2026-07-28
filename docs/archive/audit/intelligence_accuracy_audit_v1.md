
# Intelligence Accuracy & Trustworthiness Audit v1


**Generated**: 2026-06-16T05:38:12.681222+00:00

**Data Source**: `~/.gli_flow/gli_flow.db` + `outputs/runs/`

# 1. Data Inventory


**Total DB runs**: 28
**DB failure atlas entries**: 11
**Run output directories**: 75
**Runs with measurable metrics**: 74
**Runs with actual outcomes**: 74

# 2. Prediction Accuracy Audit


## 2.1 Aggregate Metrics

| Metric | Value |
| --- | --- |
| Total runs evaluated | 74 |
| Runs with actual outcomes | 74 |
| Average predicted readiness | 0.3033 |
| Readiness range | [0.3033, 0.3033] |
| Average predicted convergence | 0.5725 |
| Average prediction confidence | 0.522 |
| Confidence accuracy | 0.027 |
| Actual success rate | 0.027 |
| Actual failure rate | 0.973 |


## 2.2 Average Predicted Risks by Failure Type

| Failure Type | Average Predicted Risk (%) |
| --- | --- |
| DRC | 0.0 |
| LVS | 0.0 |
| Power | 0.0 |
| Routing | 0.0 |
| Timing | 0.0 |


## 2.3 Per-Run Prediction Details

| Run ID | Readiness | Confidence | Timing Risk | DRC Risk | Actual Success |
| --- | --- | --- | --- | --- | --- |
| run_1781160824_2a697c87_counte | 0.3033 | 0.522 | 0.0 | 0.0 | True |
| run_1781162247_850dad21_fir_to | 0.3033 | 0.522 | 0.0 | 0.0 | True |
| run_1781163051_11a3ab91_gcd | 0.3033 | 0.522 | 0.0 | 0.0 | False |
| run_1781181168_884e85cf_gcd | 0.3033 | 0.522 | 0.0 | 0.0 | False |
| run_1781181681_128e166b_uart_t | 0.3033 | 0.522 | 0.0 | 0.0 | False |
| run_1781246066_3c483cb5_uart_t | 0.3033 | 0.522 | 0.0 | 0.0 | False |
| run_1781249477_fb7c2e81_tiny_o | 0.3033 | 0.522 | 0.0 | 0.0 | False |
| run_1781249479_3f969a76_tiny_o | 0.3033 | 0.522 | 0.0 | 0.0 | False |
| run_1781249481_22e87818_tiny_o | 0.3033 | 0.522 | 0.0 | 0.0 | False |
| run_1781249483_0cbb2db9_tiny_o | 0.3033 | 0.522 | 0.0 | 0.0 | False |
| run_1781249484_d20802d5_tiny_o | 0.3033 | 0.522 | 0.0 | 0.0 | False |
| run_1781249486_9d4561d4_tiny_o | 0.3033 | 0.522 | 0.0 | 0.0 | False |
| run_1781249488_4008d6ba_counte | 0.3033 | 0.522 | 0.0 | 0.0 | False |
| run_1781254387_6b598798_uart_t | 0.3033 | 0.522 | 0.0 | 0.0 | False |
| run_1781498600_7e1fc4de_tiny_o | 0.3033 | 0.522 | 0.0 | 0.0 | False |
| run_1781498602_cf4f5f21_tiny_o | 0.3033 | 0.522 | 0.0 | 0.0 | False |
| run_1781498604_141719f8_tiny_o | 0.3033 | 0.522 | 0.0 | 0.0 | False |
| run_1781498606_809b3a3e_tiny_o | 0.3033 | 0.522 | 0.0 | 0.0 | False |
| run_1781498608_0ea71c69_tiny_o | 0.3033 | 0.522 | 0.0 | 0.0 | False |
| run_1781498610_c8438ba0_tiny_o | 0.3033 | 0.522 | 0.0 | 0.0 | False |
| run_1781498611_91f0b587_counte | 0.3033 | 0.522 | 0.0 | 0.0 | False |
| run_1781500407_ff24c605_tiny_o | 0.3033 | 0.522 | 0.0 | 0.0 | False |
| run_1781500410_40191c7d_tiny_o | 0.3033 | 0.522 | 0.0 | 0.0 | False |
| run_1781500412_bf6f4f17_tiny_o | 0.3033 | 0.522 | 0.0 | 0.0 | False |
| run_1781500414_afdb2994_tiny_o | 0.3033 | 0.522 | 0.0 | 0.0 | False |


# 3. Readiness Calibration Audit

| Metric | Value |
| --- | --- |
| Total calibrated runs | 74 |
| Mean Absolute Error (MAE) | 0.3139 |
| Root Mean Squared Error (RMSE) | 0.3203 |
| Max Error | 0.6967 |
| Min Error | 0.3033 |
| Std Error | 0.0638 |


### Per-Run Calibration Details

| Run ID | Predicted | Actual | Error |
| --- | --- | --- | --- |
| run_1781160824_2a697c87_counte | 0.3033 | True | 0.6967 |
| run_1781162247_850dad21_fir_to | 0.3033 | True | 0.6967 |
| run_1781163051_11a3ab91_gcd | 0.3033 | False | 0.3033 |
| run_1781181168_884e85cf_gcd | 0.3033 | False | 0.3033 |
| run_1781181681_128e166b_uart_t | 0.3033 | False | 0.3033 |
| run_1781246066_3c483cb5_uart_t | 0.3033 | False | 0.3033 |
| run_1781249477_fb7c2e81_tiny_o | 0.3033 | False | 0.3033 |
| run_1781249479_3f969a76_tiny_o | 0.3033 | False | 0.3033 |
| run_1781249481_22e87818_tiny_o | 0.3033 | False | 0.3033 |
| run_1781249483_0cbb2db9_tiny_o | 0.3033 | False | 0.3033 |
| run_1781249484_d20802d5_tiny_o | 0.3033 | False | 0.3033 |
| run_1781249486_9d4561d4_tiny_o | 0.3033 | False | 0.3033 |
| run_1781249488_4008d6ba_counte | 0.3033 | False | 0.3033 |
| run_1781254387_6b598798_uart_t | 0.3033 | False | 0.3033 |
| run_1781498600_7e1fc4de_tiny_o | 0.3033 | False | 0.3033 |
| run_1781498602_cf4f5f21_tiny_o | 0.3033 | False | 0.3033 |
| run_1781498604_141719f8_tiny_o | 0.3033 | False | 0.3033 |
| run_1781498606_809b3a3e_tiny_o | 0.3033 | False | 0.3033 |
| run_1781498608_0ea71c69_tiny_o | 0.3033 | False | 0.3033 |
| run_1781498610_c8438ba0_tiny_o | 0.3033 | False | 0.3033 |
| run_1781498611_91f0b587_counte | 0.3033 | False | 0.3033 |
| run_1781500407_ff24c605_tiny_o | 0.3033 | False | 0.3033 |
| run_1781500410_40191c7d_tiny_o | 0.3033 | False | 0.3033 |
| run_1781500412_bf6f4f17_tiny_o | 0.3033 | False | 0.3033 |
| run_1781500414_afdb2994_tiny_o | 0.3033 | False | 0.3033 |
| run_1781500415_db627e74_tiny_o | 0.3033 | False | 0.3033 |
| run_1781500417_e23cc088_tiny_o | 0.3033 | False | 0.3033 |
| run_1781500419_b80f989e_counte | 0.3033 | False | 0.3033 |
| run_1781502029_0963fa7b_tiny_o | 0.3033 | False | 0.3033 |
| run_1781502031_c1fac464_tiny_o | 0.3033 | False | 0.3033 |
| run_1781502033_a1109ff3_tiny_o | 0.3033 | False | 0.3033 |
| run_1781502034_216bc8b7_tiny_o | 0.3033 | False | 0.3033 |
| run_1781502036_0899766c_tiny_o | 0.3033 | False | 0.3033 |
| run_1781502038_ea1acb21_tiny_o | 0.3033 | False | 0.3033 |
| run_1781502040_1cfacd6a_counte | 0.3033 | False | 0.3033 |
| run_1781502093_5a462c11_tiny_o | 0.3033 | False | 0.3033 |
| run_1781502095_95a3b045_tiny_o | 0.3033 | False | 0.3033 |
| run_1781502097_699324db_tiny_o | 0.3033 | False | 0.3033 |
| run_1781502098_bdfa7da6_tiny_o | 0.3033 | False | 0.3033 |
| run_1781502100_54dc90e9_tiny_o | 0.3033 | False | 0.3033 |
| run_1781502102_10777c15_tiny_o | 0.3033 | False | 0.3033 |
| run_1781502104_2fb9c3d4_counte | 0.3033 | False | 0.3033 |
| run_1781504010_e734cd34_tiny_o | 0.3033 | False | 0.3033 |
| run_1781504012_2874fc19_tiny_o | 0.3033 | False | 0.3033 |
| run_1781504014_d1c9c819_tiny_o | 0.3033 | False | 0.3033 |
| run_1781504016_7ab65f4d_tiny_o | 0.3033 | False | 0.3033 |
| run_1781504017_f6222419_tiny_o | 0.3033 | False | 0.3033 |
| run_1781504019_7f3dc837_tiny_o | 0.3033 | False | 0.3033 |
| run_1781504021_3e7d4e9a_counte | 0.3033 | False | 0.3033 |
| run_1781507925_0594dfc4_counte | 0.3033 | False | 0.3033 |
| run_1781507931_5e1262a6_gcd | 0.3033 | False | 0.3033 |
| run_1781507939_63b1462b_uart_t | 0.3033 | False | 0.3033 |
| run_1781508407_8b158453_tiny_o | 0.3033 | False | 0.3033 |
| run_1781508409_41253ddf_tiny_o | 0.3033 | False | 0.3033 |
| run_1781508411_21cba997_tiny_o | 0.3033 | False | 0.3033 |
| run_1781508413_3b3eeb47_tiny_o | 0.3033 | False | 0.3033 |
| run_1781508414_adde8bb4_tiny_o | 0.3033 | False | 0.3033 |
| run_1781508416_f0282554_tiny_o | 0.3033 | False | 0.3033 |
| run_1781508418_18e00a24_counte | 0.3033 | False | 0.3033 |
| run_1781511507_c1737658_tiny_o | 0.3033 | False | 0.3033 |
| run_1781511510_e4a451d2_tiny_o | 0.3033 | False | 0.3033 |
| run_1781511512_4e61d599_tiny_o | 0.3033 | False | 0.3033 |
| run_1781511513_c129f30c_tiny_o | 0.3033 | False | 0.3033 |
| run_1781511515_83f55af6_tiny_o | 0.3033 | False | 0.3033 |
| run_1781511517_e802712c_tiny_o | 0.3033 | False | 0.3033 |
| run_1781511519_70f55138_counte | 0.3033 | False | 0.3033 |
| run_1781511601_ea4c0d66_tiny_o | 0.3033 | False | 0.3033 |
| run_1781511603_f7480832_tiny_o | 0.3033 | False | 0.3033 |
| run_1781511605_44ed7157_tiny_o | 0.3033 | False | 0.3033 |
| run_1781511607_b06a98dd_tiny_o | 0.3033 | False | 0.3033 |
| run_1781511609_d8962fda_tiny_o | 0.3033 | False | 0.3033 |
| run_1781511611_69293571_tiny_o | 0.3033 | False | 0.3033 |
| run_1781511612_a73ec54c_counte | 0.3033 | False | 0.3033 |
| run_1781586782_b4b86c77_picorv | 0.3033 | False | 0.3033 |


# 4. Similarity Usefulness Audit

| Metric | Value |
| --- | --- |
| Runs with similarity comparisons | 74 |
| Average similarity score | 0.0627 |
| Failure type agreement among similars | 0.0 |
| Similarity Usefulness Score | 0.0314 |


# 5. Recommendation Evidence Audit

| Metric | Value |
| --- | --- |
| Total recommendation types | 4 |
| With evidence | 4 |
| Without evidence | 0 |
| Average historical success rate | 0.0 |
| Average trust score | 0.6 |


### Per-Failure-Type Recommendation Evidence

| Failure Type | Recommended Fix | Success Rate | Trust Score | Evidence | Supporting Runs |
| --- | --- | --- | --- | --- | --- |
| CROSS_TOOL_DRC_DISAGREEMENT |  | 0.0 | 0.6 | YES | 4 |
| DRC_SPACING |  | 0.0 | 0.6 | YES | 2 |
| PIPELINE_FAILURE |  | 0.0 | 0.6 | YES | 3 |
| SIGNOFF_FAILURE |  | 0.0 | 0.6 | YES | 2 |


# 6. Trust Score Audit


⚠ No resolution patterns to evaluate

# 7. Knowledge Graph Fidelity Audit

| Metric | Value |
| --- | --- |
| Total DB entries | 11 |
| Total graph entities | 19 |
| Total graph relationships | 24 |
| DB entries matched in graph | 11 |
| Synthetic entities (no DB match) | 0 |
| Synthetic relationships | 0 |
| Graph clean (no synthetic links) | True |


**Relationship types**: {'occurs_in': 11, 'caused_by': 11, 'related_to': 2}

**Entity types**: {'Failure': 11, 'RootCause': 8}

# 8. Failure Atlas Signature Mapping Audit

| Metric | Value |
| --- | --- |
| Total DB entries | 11 |
| Unique signatures | 4 |
| Runs with atlas entries | 5 |
| Runs with predictions + entries | 4 |
| Failure types in DB | 4 |
| Recommendations mapped to signatures | 4 |
| Signature coverage ratio | 0.3636 |


# 9. Warehouse Consistency Audit

| Component | Records |
| --- | --- |
| DB failure_atlas_entries table | 11 |
| Warehouse execution records | 0 |
| Repository count entries() | 11 |
| DB runs table | 28 |
| Warehouse failure types | 0 |
| Repository fixed entries | 0 |


**Consensus**: CONSISTENT

# 10. False Confidence Audit

| Type | Count |
| --- | --- |
| False positives (high confidence but wrong) | 0 |
| False negatives (low confidence but right) | 0 |


# 11. Edge Case Audit

| Metric | Value |
| --- | --- |
| Total failure types | 4 |
| Single-occurrence types | 0 |
| Rare types (≤3 occurrences) | 3 |
| Low-sample resolution patterns (<5 attempts) | 0 |


### Failure Type Distribution

| Failure Type | Occurrences |
| --- | --- |
| CROSS_TOOL_DRC_DISAGREEMENT | 4 |
| PIPELINE_FAILURE | 3 |
| DRC_SPACING | 2 |
| SIGNOFF_FAILURE | 2 |


# 12. Trustworthiness Score


**Overall Trustworthiness Score**: **61.3%**

### Component Breakdown

| Component | Score | Weight | Weighted Contribution |
| --- | --- | --- | --- |
| accuracy | 2.7% | 25% | 0.7% |
| calibration | 68.6% | 15% | 10.3% |
| evidence_quality | 100.0% | 15% | 15.0% |
| consistency | 100.0% | 10% | 10.0% |
| false_confidence_penalty | 100.0% | 10% | 10.0% |
| similarity_usefulness | 3.1% | 10% | 0.3% |
| knowledge_graph_fidelity | 100.0% | 10% | 10.0% |
| edge_case_robustness | 100.0% | 5% | 5.0% |


**Rating**: FUNCTIONAL

**Assessment**: Intelligence is mostly correct but has known gaps.

# 13. Success Criteria Verification


**Target**: GLI can demonstrate that its intelligence outputs are not only data-driven but also empirically correct.

❌ Trustworthiness Score: 61.3% < 70% threshold
❌ Prediction confidence accuracy: 2.7% < 60%
✅ Calibration error: 0.3139 ≤ 0.4
✅ Recommendations with evidence: 4/4 ≥ 50%
✅ Knowledge graph has no synthetic links: True