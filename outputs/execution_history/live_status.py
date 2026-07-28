import sqlite3


DB_NAME = "gli_flow.db"


class LiveExecutionStatus:

    def __init__(self):

        self.connection = sqlite3.connect(
            DB_NAME
        )

        self.cursor = self.connection.cursor()

    def get_active_runs(self):

        self.cursor.execute("""
        SELECT *
        FROM runs
        WHERE status = 'RUNNING'
        """)

        rows = self.cursor.fetchall()

        results = []

        for row in rows:

            results.append({

                "run_id": row[0],

                "design_name": row[1],

                "current_stage": row[4],

                "status": row[3]
            })

        return results

    def close(self):

        self.connection.close()
