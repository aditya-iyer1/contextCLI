
import sqlite3
import pandas as pd
import sys

db = "state.db"
conn = sqlite3.connect(db)
try:
    df = pd.read_sql_query("SELECT * FROM predictions", conn)
    print(f"Total rows: {len(df)}")
    if not df.empty:
        print("Columns:", df.columns.tolist())
        print(df[['run_id', 'prompt_tokens', 'f1_score']].tail(20))
        
        # Check specific run
        if len(sys.argv) > 1:
            run_id = sys.argv[1]
            run_df = df[df['run_id'] == run_id]
            print(f"\nStats for {run_id}:")
            print(run_df.describe())
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
