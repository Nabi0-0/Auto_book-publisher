
import sqlite3

db_path = "chroma_db/chroma.sqlite3"

connection = sqlite3.connect(
    f"file:{db_path}?mode=ro",
    uri=True,
)

print("Tables:")
tables = connection.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()

for table in tables:
    print(table[0])

print("\nCollections schema:")
schema = connection.execute(
    "PRAGMA table_info(collections)"
).fetchall()

for column in schema:
    print(column)

print("\nCollections data:")
try:
    rows = connection.execute(
        "SELECT * FROM collections"
    ).fetchall()

    for row in rows:
        print(row)
except sqlite3.Error as error:
    print("Could not read collections:", error)

connection.close()
