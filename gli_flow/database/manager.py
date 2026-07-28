import sqlite3


class DatabaseManager:
    def __init__(self, db_path: str = "gli_flow.db"):
        self.db_path = db_path

    def get_runs(self, limit=20):
        return get_runs(self.db_path, limit)

    def execute_query(self, query: str, params=()):
        connection = sqlite3.connect(self.db_path)
        try:
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            return cursor.fetchall()
        finally:
            connection.close()


def get_runs(db_path, limit=20):
    connection = sqlite3.connect(db_path)

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT
                run_id,
                design_name,
                status,
                current_stage,
                progress,
                wns,
                tns,
                utilization,
                runtime_sec,
                cell_count,
                qor_score,
                timestamp
            FROM runs
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,)
        )

        rows = cursor.fetchall()
    finally:
        connection.close()

    results = []

    for row in rows:
        results.append({
            "run_id": row[0],
            "design_name": row[1],
            "status": row[2],
            "current_stage": row[3],
            "progress": row[4],
            "wns": row[5],
            "tns": row[6],
            "utilization": row[7],
            "runtime_sec": row[8],
            "cell_count": row[9],
            "qor_score": row[10],
            "timestamp": row[11]
        })

    return results
