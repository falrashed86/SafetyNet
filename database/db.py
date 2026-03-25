from pathlib import Path
import sqlite3

# Always use the SAME DB file no matter where Streamlit is run from
DB_PATH = Path(__file__).parent / "safetynet.db"


def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # Simple schema (NO reason column)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mode TEXT,
            stars INTEGER,
            confidence REAL,
            risk TEXT,
            text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()


def save_message(result: dict):
    """
    Save analyzer output safely (works with your current DB).
    Expects result keys like: risk, mode, confidence, stars, text/message
    """
    conn = get_conn()
    cur = conn.cursor()

    mode = result.get("mode")
    stars = result.get("stars")
    confidence = result.get("confidence")
    risk = result.get("risk")

    # Support both keys: "text" or "message"
    text = result.get("text") or result.get("message") or ""

    cur.execute(
        """
        INSERT INTO messages (mode, stars, confidence, risk, text)
        VALUES (?, ?, ?, ?, ?)
        """,
        (mode, stars, confidence, risk, text),
    )

    conn.commit()
    conn.close()


def get_counts():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM messages")
    total = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM messages WHERE UPPER(risk)='HIGH'")
    high = cur.fetchone()[0] or 0

    conn.close()
    return total, high


def get_recent_high(limit=30):
    """
    Returns rows in THIS order:
    (id, mode, stars, confidence, risk, text)

    This matches your Parent Dashboard normalizer.
    """
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, mode, stars, confidence, risk, text
        FROM messages
        WHERE UPPER(risk)='HIGH'
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_risk_counts():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT UPPER(risk), COUNT(*) FROM messages GROUP BY UPPER(risk)")
    rows = cur.fetchall()
    conn.close()

    out = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for r, c in rows:
        if r in out:
            out[r] = c
    return out
