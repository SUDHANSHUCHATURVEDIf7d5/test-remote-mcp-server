from fastmcp import FastMCP
import os
import sqlite3
import random
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")

CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

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
                            WHERE date BETWEEN ? AND ? 
                            ORDER BY id ASC""",
                            (start_date, end_date))
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


@mcp.tool()
def summarise(start_date, end_date, category=None):
    '''Summarise expenses by category within an inclusive date range.'''
    with sqlite3.connect(DB_PATH) as c:
        query = (
            """SELECT category, SUM(amount) AS tota_amount
            FROM expenses
            WHERE data between ? AND ?
            """
        )
        params = [start_date, end_date]
        if category:
            query += "AND category = ?"
            params.append(category)
        query += "GROUP BY category ORDER BY category ASC"

        cur = c.execute(query, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


@mcp.resource("expenses://categories", mime_type="application/json")
def categories():
    '''Read fresh each time so you can edit the file without restarting'''
    with open(CATEGORIES_PATH, 'r', encoding='utf-8') as f:
        return f.read()


if __name__ == "__main__":
    # mcp.run()
    mcp.run(transport="http", host="0.0.0.0", port=8080)