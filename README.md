# dykepoolreviews
Dyke Pool PDX Table Reviews (based on their IG)

Inspired by Cheeseburger World

pip3 install -r requirements.txt && python app.py

.claude/worktrees/bold-mendel-04ce94/requirements.txt


sqlite3 pool.db "PRAGMA writable_schema=ON;
UPDATE sqlite_master SET sql = replace(sql, 'CHECK(rating BETWEEN 0 AND 3)', 'CHECK(rating BETWEEN 0 AND 5)') WHERE name = 'venues';
PRAGMA writable_schema=OFF;
PRAGMA integrity_check;"

-- sqlite3 pool.db < schema.sql

-- sqlite3 .claude/worktrees/bold-mendel-04ce94/pool.db "PRAGMA writable_schema=ON;
-- UPDATE sqlite_master SET sql = replace(sql, 'CHECK(rating BETWEEN 0 AND 3)', 'CHECK(rating BETWEEN 0 AND 5)') WHERE name = 'venues';
-- PRAGMA writable_schema=OFF;
-- PRAGMA integrity_check;"