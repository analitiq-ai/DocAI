import sqlite3
import json
from doc_manager.models import Document
import threading

# Singleton connection and thread lock
connection_lock = threading.Lock()
connection = sqlite3.connect("documents.db", check_same_thread=False)

def create_table():
    global connection
    with connection_lock:  # Locking to ensure thread safety
        cursor = connection.cursor()
        # Define table schema
        cursor.execute(
            """
            create table main.documents
            (
                id            INTEGER
                    primary key autoincrement,
                summary       TEXT not null,
                category      TEXT not null,
                filepath      TEXT not null,
                text          TEXT not null,
                tags          TEXT not null,
                timestamp     TEXT not null,
                langs         TEXT not null,
                text_orig     TEXT not null,
                title         TEXT not null,
                filepath_orig TEXT,
                vdb_uuid      TEXT not null
                    constraint documents_pk
                        unique
            );
            """
        )

        # Commit changes and close connection
        connection.commit()
        connection.close()

# SQLite database operations
def add_document_db(document: Document):
    global connection
    with connection_lock:  # Locking to ensure thread safety
        cursor = connection.cursor()

        # Prepare data for insertion
        data = document.model_dump()
        data["tags"] = json.dumps(data["tags"])
        data["langs"] = json.dumps(data["langs"])

        # Insert data into the table
        cursor.execute(
            """
            INSERT INTO documents (
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

        # Commit changes and close connection
        connection.commit()
        cursor.close()

    return last_row_id

