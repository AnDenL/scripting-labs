import json
import sqlite3
from pathlib import Path

from pydantic import ValidationError

from .database import get_connection
from .schemes import CategoryCreate, RecordCreate

BASE_DIR = Path(__file__).resolve().parent
SEED_PATH = BASE_DIR / "data" / "seed.json"


def seed_database() -> None:
    if not SEED_PATH.exists():
        print(f"Error: file {SEED_PATH} not found.")
        return

    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] > 0:
            print("Database already contains data. Skipped.")
            return

        with open(SEED_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        categories_raw = data.get("categories", [])
        records_raw = data.get("records", [])

        validated_categories = [CategoryCreate(name=c["name"]) for c in categories_raw]
        validated_records = [RecordCreate(**r) for r in records_raw]

        with connection:
            for raw_cat, val_cat in zip(categories_raw, validated_categories):
                connection.execute(
                    "INSERT INTO categories (id, name) VALUES (?, ?)",
                    (raw_cat["id"], val_cat.name),
                )

            for rec in validated_records:
                connection.execute(
                    """
                    INSERT INTO records (code, title, category_id, value, status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (rec.code, rec.title, rec.category_id, rec.value, rec.status),
                )

        print("Database seeded with data!")

    except (sqlite3.Error, ValidationError, KeyError, ValueError) as e:
        print(f"Error while inserting in database, changes reverted: {e}")
    finally:
        connection.close()


if __name__ == "__main__":
    seed_database()
