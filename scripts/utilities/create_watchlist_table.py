import sqlite3
import os

# Get the database path
db_path = 'db.sqlite3'

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the Watchlist table
create_table_sql = '''
CREATE TABLE IF NOT EXISTS "StockPricePredictionApp_watchlist" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "ticker" varchar(20) NOT NULL,
    "created_at" datetime NOT NULL,
    "user_id" bigint NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("user_id", "ticker")
);
'''

cursor.execute(create_table_sql)

# Create index for foreign key
index_sql = '''
CREATE INDEX IF NOT EXISTS "StockPricePredictionApp_watchlist_user_id_idx" 
ON "StockPricePredictionApp_watchlist" ("user_id");
'''

cursor.execute(index_sql)

# Commit and close
conn.commit()

# List all tables to verify
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")

conn.close()

print("\nWatchlist table created successfully!")
