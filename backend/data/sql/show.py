import sqlite3

conn = sqlite3.connect("enterprise.db")
cursor = conn.cursor()

# 1️⃣ Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in database:")
for table in tables:
    print(table[0])

conn.close()
