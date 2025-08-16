from dotenv import load_dotenv
load_dotenv()  # load all env variables

import streamlit as st
import os
import sqlite3
import time
import google.generativeai as genai
import google.api_core.exceptions

# Absolute DB path (same as sql.py)
DB_PATH = r"C:\Users\Lenovo\OneDrive\Desktop\AI_agents\student.db"

# ✅ Ensure DB and STUDENT table exist
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS STUDENT (
            NAME TEXT,
            CLASS TEXT,
            SECTION TEXT,
            MARKS INTEGER
        )
    """)

    # Insert sample rows if table is empty
    cur.execute("SELECT COUNT(*) FROM STUDENT")
    if cur.fetchone()[0] == 0:
        sample_data = [
            ("Alice", "Data Science", "A", 85),
            ("Bob", "AI", "B", 90),
            ("Charlie", "Data Science", "A", 78),
            ("David", "ML", "C", 88),
            ("Eva", "AI", "B", 92),
        ]
        cur.executemany("INSERT INTO STUDENT (NAME, CLASS, SECTION, MARKS) VALUES (?, ?, ?, ?)", sample_data)

    conn.commit()
    conn.close()

# Run initializer
init_db()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# cleans the query
def clean_sql(query: str) -> str:
    return query.strip().replace("```sql", "").replace("```", "").strip()

# Initialize models
pro_model = genai.GenerativeModel("gemini-1.5-pro")
flash_model = genai.GenerativeModel("gemini-1.5-flash")

# Function to load google model and provide SQL query as a response
def get_gemini_response(question, prompt):
    models_to_try = [pro_model, flash_model]

    for model in models_to_try:
        for attempt in range(5):  # retry up to 5 times
            try:
                response = model.generate_content([prompt[0], question])
                if model.model_name == "models/gemini-1.5-flash":
                    st.info("⚡ Switched to Gemini Flash due to Pro model quota limits.")
                return response.text
            except google.api_core.exceptions.ResourceExhausted:
                wait_time = min(2 ** attempt, 32)
                st.warning(f"[{model.model_name}] Quota hit. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            except Exception as e:
                st.error(f"[{model.model_name}] Error: {e}")
                break  # move to next model
        st.warning(f"[{model.model_name}] failed after retries, trying next model...")

    raise Exception("All models failed due to quota or errors.")

# Function to retrieve query from database
def read_sql_query(sql):
    conn = sqlite3.connect(DB_PATH)  # always use correct DB path
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return rows

# Prompt
prompt = ["""    
    You are an expert AI assistant specializing in converting natural language questions into SQL queries.

The SQL database is named STUDENT and contains the following columns:

NAME (VARCHAR)
CLASS (VARCHAR)
SECTION (VARCHAR)
MARKS (INT)

Follow these guidelines when generating SQL queries:

- Ensure the output contains only the SQL query—no explanations or extra text.
- Use proper SQL syntax while maintaining accuracy and efficiency.
- If filtering is needed, use WHERE clauses.
- If aggregation is needed, use COUNT(), AVG(), etc.

Examples:
Question: "How many student records are present?"
SQL Query: SELECT COUNT(*) FROM STUDENT;

Question: "List all students in the Data Science class."
SQL Query: SELECT * FROM STUDENT WHERE CLASS = "Data Science";

Now, generate an SQL query for this given question.
"""]

# Streamlit app
st.set_page_config(page_title="SQL Query GENERATOR | QUERYMATE", page_icon="$")

# Display the logo and header
st.image("123.png", width=200)
st.markdown("$ ANSH'S GEMINI APP - your AI powered SQL Assistant!")
st.markdown("$ Ask any question, and I'll generate the SQL query for you!")

# User input
question = st.text_input("$ Enter your query in plain English:", key="input")

# Submit button
submit = st.button("Generate SQL Query")

# If submit is clicked
if submit and question.strip():
    try:
        sql_query = get_gemini_response(question, prompt)
        st.subheader("🔹 Generated SQL Query")
        st.code(sql_query, language="sql")

        response = read_sql_query(sql_query)
        st.subheader("📊 Query Results")
        if response:
            for row in response:
                st.write(row)
        else:
            st.info("No results found for this query.")
    except Exception as e:
        st.error(f"Error: {e}")
