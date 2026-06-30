"""
数据库模块 - SQLite 初始化和操作
"""
import sqlite3
from config import DB_PATH


def init_db():
    """创建数据库表（如果不存在）"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT NOT NULL,
        industry TEXT NOT NULL,
        scenario TEXT,
        extra TEXT,
        created_at TEXT DEFAULT (datetime('now', 'localtime'))
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        submission_id INTEGER,
        category TEXT,
        original_name TEXT,
        saved_path TEXT,
        file_type TEXT,
        file_size INTEGER,
        created_at TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (submission_id) REFERENCES submissions(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS knowledge_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        submission_id INTEGER,
        file_id INTEGER,
        entry_type TEXT,
        title TEXT,
        content TEXT,
        metadata TEXT,
        created_at TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (submission_id) REFERENCES submissions(id),
        FOREIGN KEY (file_id) REFERENCES files(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS company_kb_map (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT NOT NULL UNIQUE,
        kb_id TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now', 'localtime'))
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS pushed_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT NOT NULL,
        filename TEXT NOT NULL,
        file_size INTEGER,
        kb_id TEXT,
        created_at TEXT DEFAULT (datetime('now', 'localtime')),
        UNIQUE(company, filename, file_size)
    )""")
    conn.commit()
    conn.close()


def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
