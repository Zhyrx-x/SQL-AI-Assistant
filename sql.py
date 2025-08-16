import sqlite3
import os

#clean the query
def clean_sql(query: str) -> str:
    return query.strip().replace("```sql", "").replace("```", "").strip()

# Absolute path to your DB file
DB_PATH = r"C:\Users\Lenovo\OneDrive\Desktop\AI_agents\student.db"

# Ensure the folder exists
if not os.path.exists(os.path.dirname(DB_PATH)):
    raise FileNotFoundError("The folder for the database does not exist.")

# Connect safely
connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

# Create the table safely
table_info = """
CREATE TABLE IF NOT EXISTS STUDENT(
    NAME VARCHAR(25),
    CLASS VARCHAR(25),
    SECTION VARCHAR(25),
    MARKS INT
);
"""
cursor.execute(table_info)

# Insert records only if table is empty (to avoid duplicates)
cursor.execute("SELECT COUNT(*) FROM STUDENT")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO STUDENT VALUES ('ansh', 'genai', 'A', 90)")
    cursor.execute("INSERT INTO STUDENT VALUES ('rahul', 'ML', 'B', 50)")
    cursor.execute("INSERT INTO STUDENT VALUES ('yash', 'genai--', 'C', 80)")
    cursor.execute("INSERT INTO STUDENT VALUES ('uday', 'genai++', 'D', 70)")
    cursor.execute("INSERT INTO STUDENT VALUES ('amuj', 'dgenai', 'E', 60)")

# Display records
print("The records in STUDENT table are:")
data = cursor.execute("SELECT * FROM STUDENT")
for row in data:
    print(row)

connection.commit()
connection.close()
