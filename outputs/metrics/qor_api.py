import sqlite3


DATABASE_PATH = "gli_flow.db"


def get_connection():

    return sqlite3.connect(
        DATABASE_PATH
    )


def get_all_runs():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""

    SELECT
        run_id,
        design_name,
        toolchain,
        status,
        current_stage,
        runtime_sec,
        wns,
        tns,
        utilization,
        cell_count,
        timestamp

    FROM runs

    ORDER BY timestamp DESC

    """)

    rows = cursor.fetchall()

    connection.close()

    results = []

    for row in rows:

        results.append({

            "run_id": row[0],

            "design_name": row[1],

            "toolchain": row[2],

            "status": row[3],

            "current_stage": row[4],

            "runtime_sec": row[5],

            "wns": row[6],

            "tns": row[7],

            "utilization": row[8],

            "cell_count": row[9],

            "timestamp": row[10]
        })

    return results


def get_latest_run():

    runs = get_all_runs()

    if len(runs) == 0:

        return {}

    return runs[0]


def get_live_runs():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""

    SELECT
        run_id,
        current_stage,
        status

    FROM runs

    WHERE status = 'RUNNING'

    """)

    rows = cursor.fetchall()

    connection.close()

    results = []

    for row in rows:

        results.append({

            "run_id": row[0],

            "current_stage": row[1],

            "status": row[2]
        })

    return results


def get_wns_trend():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""

    SELECT
        timestamp,
        wns

    FROM runs

    ORDER BY timestamp ASC

    """)

    rows = cursor.fetchall()

    connection.close()

    return rows
