import sqlite3
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Apply SQLite schema to database")
    parser.add_argument("--db", "-d", required=True, help="Path to the SQLite database file")
    args = parser.parse_args()
    
    # Path to your target DB (from command line argument)
    db_path = args.db
    # Path to the schema file
    schema_path = os.path.join(os.path.dirname(__file__), "config", "schema_offline.sql")

    # Ensure the DB file exists (or create it)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Read and execute all SQL from the schema file
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        cursor.executescript(schema_sql)

    conn.commit()
    conn.close()
    print(f"Schema applied to {db_path}")

if __name__ == "__main__":
    main()
