from fastmcp import FastMCP
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")

mcp = FastMCP("ExpenseTracker")

def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """)

init_db()

@mcp.tool()
def add_expenses(date, amount, category, subcategory="", note=""):
    '''Add a new expense in the database.'''
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "INSERT INTO expenses(date, amount, category, subcategory, note)" \
            "VALUES (?,?,?,?,?)", (date, amount, category, subcategory, note)
        )
        return {"status":"ok", "id":cur.lastrowid}

@mcp.tool()
def list_expenses(start_date, end_date):
    '''List all the expenses present in the database.'''
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute("""SELECT id, date, amount, category, subcategory, note 
                            FROM expenses 
                            WHERE date BETWEEM ? AND ? 
                            ORDER BY id ASC""",
                            (start_date, end_date))
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


if __name__ == "__main__":
    mcp.run()