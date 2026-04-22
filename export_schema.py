"""
Run this any time you want schema.sql to reflect the current approved venues:

    python export_schema.py
"""

import os
import sqlite3

DATABASE = os.path.join(os.path.dirname(__file__), "pool.db")
SCHEMA   = os.path.join(os.path.dirname(__file__), "schema.sql")

HEADER = """\
DROP TABLE IF EXISTS venues;
CREATE TABLE venues (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_name     TEXT    NOT NULL,
    location       TEXT    NOT NULL,
    num_tables     INTEGER NOT NULL DEFAULT 1,
    price_per_game TEXT    NOT NULL,
    bathroom_type  TEXT    NOT NULL,
    rating         INTEGER NOT NULL DEFAULT 1 CHECK(rating BETWEEN 0 AND 5),
    notes          TEXT,
    photo_URL      TEXT,
    status         TEXT    NOT NULL DEFAULT 'approved',
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def q(val):
    """Quote a value for SQL."""
    if val is None:
        return "NULL"
    return "'" + str(val).replace("'", "''") + "'"

db = sqlite3.connect(DATABASE)
db.row_factory = sqlite3.Row
venues = db.execute(
    "SELECT * FROM venues WHERE status = 'approved' ORDER BY id"
).fetchall()
db.close()

lines = [HEADER]
for v in venues:
    lines.append(
        f"INSERT OR IGNORE INTO venues "
        f"(id, venue_name, location, num_tables, price_per_game, bathroom_type, rating, notes, photo_url, status) "
        f"VALUES ({v['id']}, {q(v['venue_name'])}, {q(v['location'])}, {v['num_tables']}, "
        f"{q(v['price_per_game'])}, {q(v['bathroom_type'])}, {v['rating']}, "
        f"{q(v['notes'])}, {q(v['photo_url'])}, 'approved');"
    )

with open(SCHEMA, "w") as f:
    f.write("\n".join(lines) + "\n")

print(f"schema.sql updated — {len(venues)} approved venue{'s' if len(venues) != 1 else ''} exported.")
