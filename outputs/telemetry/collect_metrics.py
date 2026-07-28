import os


def parse_reports(run_dir):

    metrics = {

        "wns": None,

        "tns": None,

        "utilization": None,

        "runtime_sec": None,

        "cell_count": None
    }

    timing_report = (
        f"{run_dir}/reports/timing.rpt"
    )

    utilization_report = (
        f"{run_dir}/reports/utilization.rpt"
    )

    runtime_report = (
        f"{run_dir}/reports/runtime.rpt"
    )

    # TIMING REPORT

    if os.path.exists(timing_report):

        with open(timing_report, "r") as file:

            lines = file.readlines()

            for line in lines:

                if "WNS:" in line:

                    metrics["wns"] = float(
                        line.split(":")[1].strip()
                    )

                if "TNS:" in line:

                    metrics["tns"] = float(
                        line.split(":")[1].strip()
                    )

    # UTILIZATION REPORT

    if os.path.exists(utilization_report):

        with open(
            utilization_report,
            "r"
        ) as file:

            lines = file.readlines()

            for line in lines:

                if "Core Utilization:" in line:

                    value = (
                        line
                        .split(":")[1]
                        .replace("%", "")
                        .strip()
                    )

                    metrics["utilization"] = (
                        float(value)
                    )

                if "Total Cells:" in line:

                    metrics["cell_count"] = int(
                        line.split(":")[1].strip()
                    )

    # RUNTIME REPORT

    if os.path.exists(runtime_report):

        with open(runtime_report, "r") as file:

            lines = file.readlines()

            for line in lines:

                if "Total Runtime:" in line:

                    value = (
                        line
                        .split(":")[1]
                        .replace("sec", "")
                        .strip()
                    )

                    metrics["runtime_sec"] = (
                        float(value)
                    )

    return metrics
