import sqlite3
from contextlib import closing
from config import DB_PATH

CREATE_MESSAGES_SQL = '''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    file_path TEXT,
    subject TEXT,
    sender TEXT,
    recipients TEXT,
    msg_date TEXT,
    body TEXT
);
'''

CREATE_FTS_SQL = '''
-- try to create FTS5 virtual table; if unavailable SQL error will be raised
CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(subject, sender, recipients, body, content='');
'''

def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute(CREATE_MESSAGES_SQL)
        try:
            cur.execute(CREATE_FTS_SQL)
        except sqlite3.OperationalError:
            # FTS5가 없으면 그냥 넘어감; 검색에서 LIKE로 대체
            pass
        conn.commit()

def insert_message(file_path, subject, sender, recipients, msg_date, body):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO messages (file_path, subject, sender, recipients, msg_date, body) VALUES (?, ?, ?, ?, ?, ?)',
                    (file_path, subject, sender, recipients, msg_date, body))
        rowid = cur.lastrowid
        try:
            cur.execute('INSERT INTO messages_fts(rowid, subject, sender, recipients, body) VALUES (?, ?, ?, ?, ?)',
                        (rowid, subject or '', sender or '', recipients or '', body or ''))
        except sqlite3.OperationalError:
            # FTS 미지원시 무시
            pass
        conn.commit()
        return rowid

def search(query):
    q = query.strip()
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        # 우선 FTS5가 있으면 FTS로 검색
        try:
            cur.execute("SELECT m.id, m.subject, m.sender, m.msg_date FROM messages m JOIN messages_fts f ON f.rowid=m.id WHERE messages_fts MATCH ? LIMIT 200", (q,))
            rows = cur.fetchall()
            return rows
        except sqlite3.OperationalError:
            # FTS 미지원 -> LIKE 검색
            like_q = f"%{q}%"
            cur.execute("SELECT id, subject, sender, msg_date FROM messages WHERE subject LIKE ? OR body LIKE ? OR sender LIKE ? LIMIT 200", (like_q, like_q, like_q))
            return cur.fetchall()

def get_message(message_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, file_path, subject, sender, recipients, msg_date, body FROM messages WHERE id=?', (message_id,))
        return cur.fetchone()

def list_messages_under_folder(folder_prefix):
    # folder_prefix는 절대경로 혹은 파일 경로의 prefix
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        like_q = f"{folder_prefix}%"
        cur.execute('SELECT id, file_path, subject, sender, msg_date FROM messages WHERE file_path LIKE ? LIMIT 1000', (like_q,))
        return cur.fetchall()
