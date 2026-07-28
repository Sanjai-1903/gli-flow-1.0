def generate_gap_report(runs, baseline=None):
    return {
        "total_runs": len(runs),
        "baseline": baseline,
        "gaps": []
    }
