import sqlite3
import json
import threading
from doc_ai.configs.models import Document

class DocumentDatabase:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DocumentDatabase, cls).__new__(cls)
                cls._instance._init_db(db_path)
        return cls._instance

    def _init_db(self, db_path):
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection_lock = threading.Lock()

    def create_table(self, table_name = 'documents'):
        with self.connection_lock:
            cursor = self.connection.cursor()
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    summary       TEXT NOT NULL,
                    category      TEXT NOT NULL,
                    filepath      TEXT NOT NULL,
                    text          TEXT NOT NULL,
                    tags          TEXT NOT NULL,
                    timestamp     TEXT NOT NULL,
                    langs         TEXT NOT NULL,
                    text_orig     TEXT NOT NULL,
                    title         TEXT NOT NULL,
                    filepath_orig TEXT,
                    vdb_uuid      TEXT NOT NULL UNIQUE
                );
                """
            )
            self.connection.commit()

    def add_document(self, document: Document, table_name = 'documents'):
        with self.connection_lock:
            cursor = self.connection.cursor()
            data = document.model_dump()
            data["tags"] = json.dumps(data["tags"])
            data["langs"] = json.dumps(data["langs"])

            cursor.execute(
                f"""
                INSERT INTO {table_name} (
                    title, summary, text, text_orig, category,
                    filepath, tags, timestamp, langs, filepath_orig, vdb_uuid
                )
                VALUES (
                    :title, :summary, :text, :text_orig, :category,
                    :filepath, :tags, :timestamp, :langs, :filepath_orig, :uuid
                )
                """,
                data,
            )
            last_row_id = cursor.lastrowid
            self.connection.commit()
            return last_row_id
