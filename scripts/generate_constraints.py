def generate_timing_constraints(design_name, clock_period_ns=10.0):
    return {
        "design": design_name,
        "clock_period_ns": clock_period_ns,
        "constraints": []
    }
