import sqlite3
from dataclasses import dataclass
from typing import Protocol, Iterator, Sequence, Callable, Type
from pathlib import Path

import pydantic


@dataclass(slots=True)
class Row[T: pydantic.BaseModel]:
    id: int
    created: str
    modified: str
    data: T


class QueryType(Protocol):
    where: Callable[[None], str] | None
    groupby: Callable[[None], str] | None
    orderby: Callable[[None], str] | None
    limit: Callable[[None], int] | None
    offset: Callable[[None], int] | None


class Paginated[T](Protocol):
    def __iter__(self) -> Iterator[Sequence[T]]: ...
    def __next__(self) -> Sequence[T]: ...


class StoreType[T: pydantic.BaseModel](Protocol):
    schema: Type[T]
    def init(self) -> None:
        "Initialise the store. Connect to databases, create tables, etc."
    def create(self, *args) -> Row[T]:
        "Create a row in the store."
    def read(self, query: QueryType | None = None) -> Paginated[Row[T]]:
        "Retrieve rows from the store that satisfy the query."
    def update(self, id: int, data: T) -> Row[T]:
        "Update the specified row in the store."
    def delete(self, id: int) -> Row[T]:
        "Delete the specified row from the store."


class SQLiteStore[T: pydantic.BaseModel]:
    schema: Type[T]
    def __init__(self, *connection_args) -> None: ...  # TODO
    def init(self) -> None: ...  # TODO
    def create(self, *args) -> Row[T]: ...  # TODO
    def read(self, query: QueryType | None = None) -> Paginated[Row[T]]: ...  # TODO
    def update(self, id: int, data: T) -> Row[T]: ...  # TODO
    def delete(self, id: int) -> Row[T]: ...  # TODO


class AISQLiteStore[T]:
    schema: Type[T]
    connection: sqlite3.Connection

    def __init__(self, *args) -> None:
        self.connection_args = args

    def init(self) -> None:
        self.connection = sqlite3.connect(*self.connection_args)
        table_name = self.schema.__name__.lower() + "s"
        self.connection.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                modified TEXT,
                data TEXT NOT NULL,
                CHECK (json_type(data) == 1)
            );
        """)
        self.connection.commit()

    def create(self, *args, **data) -> Row[T]:
        # Convert data to JSON before storing
        data_json = data.get("data").json()
        cursor = self.conn.cursor()
        cursor.execute(f"""
            INSERT INTO {self.schema.__name__.lower() + "s"} (data) VALUES (?)
        """, (data_json,))
        self.conn.commit()
        new_id = cursor.lastrowid
        return Row(id=new_id, created=datetime.datetime.now().isoformat(), modified=datetime.datetime.now().isoformat(), data=self.schema(**data))

    def read(self, query: QueryType | None = None) -> Paginated[Row[T]]:
        where_clause, order_by, limit, offset = "", "", None, None
        if query:
            if query.where:
                where_clause = f" WHERE {query.where()}"
            if query.orderby:
                order_by = f" ORDER BY {query.orderby()}"
            if query.limit:
                limit = query.limit()
            if query.offset:
                offset = query.offset()

        cursor = self.conn.cursor()
        cursor.execute(f"""
            SELECT id, created, modified, data FROM {self.schema.__name__.lower() + "s"}
            {where_clause} {order_by} LIMIT {limit} OFFSET {offset}
        """)
        rows = cursor.fetchall()

        def paginator():
            while rows:
                yield [Row(id=row[0], created=row[1], modified=row[2], data=self.schema.parse_raw(row[3])) for row in rows]
                rows = cursor.fetchmany(limit)

        return paginator()

    def update(self, id: int, data: T) -> Row[T]:
        # Convert data to JSON before storing
        data_json = data.json()
        cursor = self.conn.cursor()
        cursor.execute(f"""
            UPDATE {self.schema.__name__.lower() + "s"} SET data = ?, modified = CURRENT_TIMESTAMP WHERE id = ?
        """, (data_json, id))
        self.conn.commit()
        return Row(id=id, created=datetime.datetime.now().isoformat(), modified=datetime.datetime.now().isoformat(), data=data)

    def delete(self, id: int) -> Row[T]:
        cursor = self.conn.cursor()
        cursor.execute(f"""
            DELETE FROM {self.schema.__name__.lower() + "s"} WHERE id = ?
        """, (id,))
        self.conn.commit()
        # Deleted row doesn't have data, set to None
        return Row(id=id, created=None, modified=None, data=None)


DB_PATH = ':memory:'

class Store:
    def __init__(self, db: Path | str = DB_PATH):
        db = str(db.resolve()) if isinstance(db, Path) else db
        self.connection = sqlite3.connect(db)

    def __enter__(self):
        return self.connection.__enter__()

    def __exit__(self):
        return self.connection.__exit__()
