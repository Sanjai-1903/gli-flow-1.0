# Structural Metadata Study

> Privacy-safe structural metadata for future ML without reconstructing customer IP.
> Generated: 2026-06-15

---

## 1. OBJECTIVE

Identify structural metadata that:
- Is useful for QoR prediction, flow optimization, and graph intelligence
- Cannot be used to reconstruct customer RTL, netlists, or GDS
- Respects the invariant: **Never collect customer IP**

---

## 2. METADATA CATEGORIES

### 2.1 Logic Depth Distribution

| Property | Value |
|----------|-------|
| **Description** | Histogram of logic levels between flip-flops in the design |
| **Collection** | Can be extracted from timing reports (arrival time / clock period) |
| **Privacy Risk** | **LOW** — depth distribution is a summary statistic |
| **Usefulness** | **HIGH** — correlates with timing closure difficulty, optimal synthesis strategy |
| **Reconstruction risk** | Cannot reconstruct RTL from depth histogram — many designs share similar depth profiles |
| **Classification** | **SAFE** — aggregate histogram |

Example:
```json
{
  "logic_depth_histogram": {
    "buckets": [0, 5, 10, 15, 20, 25, 30, 50, 100],
    "counts": [120, 450, 890, 340, 120, 45, 12, 3]
  }
}
```

### 2.2 Fanout Distribution

| Property | Value |
|----------|-------|
| **Description** | Histogram of net fanout across the design |
| **Collection** | Can be extracted from STA reports or netlist traversal (local, no upload) |
| **Privacy Risk** | **LOW** — fanout distribution is a generic characteristic |
| **Usefulness** | **HIGH** — predicts congestion, routing difficulty, buffer insertion needs |
| **Reconstruction risk** | Fanout histogram reveals nothing about logic function |
| **Classification** | **SAFE** — aggregate histogram |

Example:
```json
{
  "fanout_histogram": {
    "buckets": [1, 2, 4, 8, 16, 32, 64, 128],
    "counts": [200, 1500, 3200, 1800, 400, 80, 15]
  }
}
```

### 2.3 Congestion Distribution

| Property | Value |
|----------|-------|
| **Description** | Per-region congestion map (percentage of overflowing routing tracks) |
| **Collection** | From route stage reports (local extraction) |
| **Privacy Risk** | **LOW-MEDIUM** — depends on granularity |
| **Usefulness** | **HIGH** — directly indicates routability issues |
| **Reconstruction risk** | Low-resolution congestion maps cannot reconstruct layout; high-resolution could hint at structure |
| **Classification** | **DERIVE** — use coarse grid (16×16 or 32×32 max) |

Safe granularity: max 32×32 grid = 1024 cells. Each cell is a single percentage value. Cannot reconstruct GDS.

```json
{
  "congestion_map": {
    "grid_size": [16, 16],
    "overflow_pct": [5.2, 3.1, 8.7, ...]
  }
}
```

### 2.4 Macro Count and Type

| Property | Value |
|----------|-------|
| **Description** | Count of hard macros (SRAMs, ROMs, PHYs, PLLs) and their aspect ratios |
| **Collection** | From floorplan/placement reports |
| **Privacy Risk** | **LOW** — macro count and size ranges are generic |
| **Usefulness** | **HIGH** — macro placement drives floorplan strategy |
| **Reconstruction risk** | Cannot reconstruct memory contents or functionality from count + size |
| **Classification** | **SAFE** — aggregate counts and size ranges |

```json
{
  "macro_count": 8,
  "macro_area_histogram": {
    "buckets_um2": [0, 1000, 10000, 100000, 1000000],
    "counts": [0, 2, 4, 1, 1]
  },
  "total_macro_area_um2": 450000,
  "std_cell_area_um2": 1200000
}
```

### 2.5 Memory Instance Count

| Property | Value |
|----------|-------|
| **Description** | Count of memory instances (SRAMs, register files) |
| **Collection** | From floorplan reports or synthesis logs |
| **Privacy Risk** | **LOW** — memory count alone is not identifying |
| **Usefulness** | **MEDIUM** — memory count is one signal for power estimation |
| **Reconstruction risk** | Memory count with no addressing information cannot reconstruct memory contents |
| **Classification** | **SAFE** — single integer |

```json
{
  "memory_instance_count": 24,
  "total_memory_bits": 131072
}
```

### 2.6 Resource Utilization Breakdown

| Property | Value |
|----------|-------|
| **Description** | Per-resource-type utilization (combinational cells, sequential cells, memories, DSPs, IOs) |
| **Collection** | From synthesis/log reports |
| **Privacy Risk** | **LOW** — cell type counts are generic |
| **Usefulness** | **HIGH** — predicts power, area, and synthesis strategy |
| **Reconstruction risk** | Cell count by type with no connectivity is useless for reconstruction |
| **Classification** | **SAFE** — aggregate counts |

```json
{
  "cell_type_counts": {
    "combinational": 45000,
    "sequential": 8500,
    "clock_gating": 120,
    "delay": 80,
    "icg": 120
  },
  "pin_count": 256,
  "io_count": 64
}
```

### 2.7 Timing Path Distribution

| Property | Value |
|----------|-------|
| **Description** | Histogram of slack values across all timing paths |
| **Collection** | From STA reports (timing.rpt, metrics.csv) |
| **Privacy Risk** | **LOW** — slack histogram is a performance metric |
| **Usefulness** | **VERY HIGH** — directly indicates timing closure status |
| **Reconstruction risk** | Slack distribution reveals zero about logic function |
| **Classification** | **SAFE** — histogram |

```json
{
  "setup_slack_histogram": {
    "buckets_ns": [-5, -1, -0.5, -0.1, 0, 0.1, 0.5, 1, 5],
    "path_counts": [0, 3, 15, 45, 120, 340, 890, 1500],
    "worst_wns": -0.85,
    "total_tns": -45.2,
    "violating_paths": 63
  },
  "hold_slack_histogram": { ... }
}
```

### 2.8 Rent Rule Approximation

| Property | Value |
|----------|-------|
| **Description** | Rent exponent r estimated from (partition size vs. pin count) at one or two cut levels |
| **Collection** | Requires netlist traversal — must be computed locally, never upload raw netlist connectivity |
| **Privacy Risk** | **LOW** — a single Rent exponent is a very coarse aggregate (typical range 0.3–0.8) |
| **Usefulness** | **MEDIUM** — predicts wirelength distribution, optimal floorplan aspect ratio |
| **Reconstruction risk** | A single scalar value cannot reconstruct netlist topology |
| **Classification** | **DERIVE** — compute locally, upload only the exponent |

```json
{
  "rent_exponent": 0.62,
  "rent_r_squared": 0.94,
  "partition_levels": 3
}
```

### 2.9 Clock Domain Count and Structure

| Property | Value |
|----------|-------|
| **Description** | Number of clock domains and approximate clock topology (leaf count) |
| **Collection** | From STA/timing reports |
| **Privacy Risk** | **LOW-MEDIUM** — depends on detail |
| **Usefulness** | **HIGH** — clock structure drives power, timing, and CTS strategy |
| **Reconstruction risk** | Clock domain count and leaf count cannot reconstruct clock gating logic |
| **Classification** | **SAFE** — aggregate counts |

```json
{
  "clock_domain_count": 3,
  "clock_leaf_count": 4500,
  "max_clock_depth": 12,
  "has_derived_clocks": true
}
```

### 2.10 Power Distribution

| Property | Value |
|----------|-------|
| **Description** | Power breakdown by category (internal, switching, leakage) and by clock domain |
| **Collection** | From power reports |
| **Privacy Risk** | **LOW** — power numbers are aggregate performance metrics |
| **Usefulness** | **HIGH** — power optimization strategy depends on dominant power type |
| **Reconstruction risk** | Cannot reconstruct RTL from power distribution |
| **Classification** | **SAFE** — currently collected |

---

## 3. RISK MATRIX

| Metadata | Privacy Risk | Usefulness | Classification | Reconstruction Concern |
|----------|-------------|------------|---------------|----------------------|
| Logic depth histogram | LOW | HIGH | SAFE | None |
| Fanout histogram | LOW | HIGH | SAFE | None |
| Congestion distribution (coarse) | LOW | HIGH | DERIVE | 16×16 grid is safe |
| Macro count + area | LOW | HIGH | SAFE | None |
| Memory instance count | LOW | MEDIUM | SAFE | None |
| Resource utilization | LOW | HIGH | SAFE | None |
| Timing path distribution | LOW | VERY HIGH | SAFE | None |
| Rent exponent | LOW | MEDIUM | DERIVE | Single scalar |
| Clock domain structure | LOW-MEDIUM | HIGH | SAFE | Aggregated |
| Power distribution | LOW | HIGH | SAFE | Already collected |
| Cell instance paths | **HIGH** | MEDIUM | **BLOCK** | Reveals design hierarchy |
| Net names | **HIGH** | MEDIUM | **BLOCK** | Could hint at function |
| Register names | **HIGH** | LOW | **BLOCK** | Reveals design intent |
| I/O port names | **HIGH** | LOW | **BLOCK** | Reveals interface |

---

## 4. RECOMMENDED COLLECTION STRATEGY

### Phase 1 (Current — Already Collected)
- WNS, TNS, Hold WNS, Hold TNS
- Utilization
- Cell count
- Runtime
- QoR score
- Power (die area, internal, switching, leakage)
- DRC/LVS counts

### Phase 2 (Add Now — Safe, High Value)
- Timing path distribution histogram (setup + hold)
- Resource utilization breakdown (combinational, sequential, clock, IO)
- Clock domain count + leaf count
- Macro count + area histogram

### Phase 3 (Add After Validation — Safe, Lower Cost-Benefit)
- Logic depth histogram
- Fanout histogram
- Coarse congestion distribution (16×16 grid)
- Memory instance count + bit count

### Phase 4 (Research Required — Privacy Review Needed)
- Rent exponent (requires netlist traversal, must be local-only compute)
- Fine-grained congestion (32×32+ grid — privacy review needed)
- Clock topology depth

---

## 5. PRIVACY DESIGN RULES

1. **Always aggregate** — never upload raw per-cell or per-net data
2. **Bin coarsely** — use logarithmic or at most 10-bin histograms
3. **No connectivity upload** — never upload adjacency, netlist topology, or pin mappings
4. **Compute locally** — run structural analysis on user's machine; upload only the derived statistics
5. **Review each new metric** — before adding a structural metric, verify it cannot be combined with other metrics to reconstruct design elements
6. **Document reconstruction risk** — for each structural metric, document what it could reveal if combined with other leaked data
