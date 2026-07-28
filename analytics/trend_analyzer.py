import sqlite3
import statistics


def analyze_trends():

    connection = sqlite3.connect(
        "gli_flow.db"
    )

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            qor_score,
            wns,
            tns,
            utilization,
            runtime_sec
        FROM runs
        WHERE status='COMPLETED'
        ORDER BY timestamp ASC
    """)

    rows = cursor.fetchall()

    connection.close()

    if len(rows) < 2:

        return {
            "status": "NOT_ENOUGH_DATA"
        }

    qor_scores = [r[0] for r in rows]
    wns_values = [r[1] for r in rows]
    runtimes = [r[4] for r in rows]

    latest_qor = qor_scores[-1]
    earliest_qor = qor_scores[0]

    qor_delta = round(
        latest_qor - earliest_qor,
        3
    )

    avg_qor = round(
        statistics.mean(qor_scores),
        3
    )

    avg_runtime = round(
        statistics.mean(runtimes),
        2
    )

    trend_direction = "STABLE"

    if qor_delta > 0.03:

        trend_direction = "IMPROVING"

    elif qor_delta < -0.03:

        trend_direction = "REGRESSING"

    return {
        "trend": trend_direction,
        "qor_delta": qor_delta,
        "average_qor": avg_qor,
        "average_runtime": avg_runtime,
        "latest_wns": wns_values[-1],
        "total_runs": len(rows)
    }
