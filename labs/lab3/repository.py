import sqlite3

from .database import get_connection
from .schemes import (
    CategoryCreate,
    CategoryRead,
    RecordCreate,
    RecordRead,
    RecordReplace,
)


def create_category(category_in: CategoryCreate) -> CategoryRead:
    connection = get_connection()
    try:
        cursor = connection.cursor()
        with connection:
            cursor.execute(
                "INSERT INTO categories (name) VALUES (?)",
                (category_in.name,),
            )
            cat_id = cursor.lastrowid
            assert cat_id is not None, "Failed to insert row and retrieve ID"

            return CategoryRead(id=cat_id, name=category_in.name)
    finally:
        connection.close()


def get_categories() -> list[CategoryRead]:
    connection = get_connection()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("SELECT id, name FROM categories ORDER BY id ASC")
        return [CategoryRead.model_validate(dict(row)) for row in cursor.fetchall()]
    finally:
        connection.close()


def delete_category(category_id: int) -> bool:
    connection = get_connection()
    try:
        cursor = connection.cursor()

        cursor.execute("SELECT id FROM categories WHERE id = ?", (category_id,))
        if not cursor.fetchone():
            return False

        cursor.execute(
            "SELECT COUNT(*) FROM records WHERE category_id = ?",
            (category_id,),
        )
        if cursor.fetchone()[0] > 0:
            raise ValueError("Impossible to delete category, that contains records.")

        with connection:
            cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))

        return True
    finally:
        connection.close()


def get_record_by_id(record_id: int) -> RecordRead | None:
    connection = get_connection()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name AS category_name
            FROM records r
            JOIN categories c ON r.category_id = c.id
            WHERE r.id = ?
            """,
            (record_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return RecordRead.model_validate(dict(row))
    finally:
        connection.close()


def create_record(record_in: RecordCreate) -> RecordRead | None:
    connection = get_connection()
    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id FROM categories WHERE id = ?", (record_in.category_id,)
        )
        if not cursor.fetchone():
            raise ValueError(f"Категорію з id={record_in.category_id} не знайдено.")

        with connection:
            cursor.execute(
                """
                INSERT INTO records (code, title, category_id, value, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    record_in.code,
                    record_in.title,
                    record_in.category_id,
                    record_in.value,
                    record_in.status,
                ),
            )
            rec_id = cursor.lastrowid

        return get_record_by_id(rec_id) if rec_id else None
    finally:
        connection.close()


def get_records(
    category_id: int | None = None,
    status: str | None = None,
    min_value: float | None = None,
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[RecordRead]:
    connection = get_connection()
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        query = """
            SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name AS category_name
            FROM records r
            JOIN categories c ON r.category_id = c.id
        """
        conditions = []
        params = []

        if category_id is not None:
            conditions.append("r.category_id = ?")
            params.append(category_id)

        if status is not None:
            conditions.append("r.status = ?")
            params.append(status)

        if min_value is not None:
            conditions.append("r.value >= ?")
            params.append(min_value)

        if q is not None:
            conditions.append("instr(r.title, ?) > 0")
            params.append(q)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY r.id ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        return [RecordRead.model_validate(dict(row)) for row in cursor.fetchall()]
    finally:
        connection.close()


def update_record(record_id: int, record_in: RecordReplace) -> RecordRead | None:
    connection = get_connection()
    try:
        cursor = connection.cursor()

        cursor.execute("SELECT id FROM records WHERE id = ?", (record_id,))
        if not cursor.fetchone():
            return None

        cursor.execute(
            "SELECT id FROM categories WHERE id = ?", (record_in.category_id,)
        )
        if not cursor.fetchone():
            raise ValueError(f"Категорію з id={record_in.category_id} не знайдено.")

        with connection:
            cursor.execute(
                """
                UPDATE records
                SET code = ?, title = ?, category_id = ?, value = ?, status = ?
                WHERE id = ?
                """,
                (
                    record_in.code,
                    record_in.title,
                    record_in.category_id,
                    record_in.value,
                    record_in.status,
                    record_id,
                ),
            )

        return get_record_by_id(record_id)
    finally:
        connection.close()


def delete_record(record_id: int) -> bool:
    connection = get_connection()
    try:
        cursor = connection.cursor()

        cursor.execute("SELECT id FROM records WHERE id = ?", (record_id,))
        if not cursor.fetchone():
            return False

        with connection:
            cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))

        return True
    finally:
        connection.close()


def create_records_batch(
    records_in: list[RecordCreate],
) -> list[RecordRead]:
    codes = [r.code for r in records_in]
    if len(codes) != len(set(codes)):
        raise ValueError("Duplicated code found in package")

    connection = get_connection()
    try:
        cursor = connection.cursor()
        created_ids = []

        with connection:
            for rec in records_in:
                cursor.execute(
                    "SELECT id FROM categories WHERE id = ?", (rec.category_id,)
                )
                if not cursor.fetchone():
                    raise ValueError(
                        f"Couldn't find category with id={rec.category_id}."
                    )

                cursor.execute(
                    """
                    INSERT INTO records (code, title, category_id, value, status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (rec.code, rec.title, rec.category_id, rec.value, rec.status),
                )
                created_ids.append(cursor.lastrowid)

        result: list[RecordRead] = []
        for rid in created_ids:
            rec = get_record_by_id(rid)
            if rec:
                result.append(rec)
        return result
    finally:
        connection.close()
