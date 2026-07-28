import sqlite3


DB_NAME = "gli_flow.db"


class ExecutionHistoryAPI:

    def __init__(self):

        self.connection = sqlite3.connect(
            DB_NAME
        )

        self.cursor = self.connection.cursor()

    def get_all_runs(self):

        self.cursor.execute("""
        SELECT *
        FROM runs
        ORDER BY timestamp DESC
        """)

        rows = self.cursor.fetchall()

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

    def get_latest_run(self):

        self.cursor.execute("""
        SELECT *
        FROM runs
        ORDER BY timestamp DESC
        LIMIT 1
        """)

        row = self.cursor.fetchone()

        if not row:

            return None

        return {

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
        }

    def close(self):

        self.connection.close()
