import contextlib
import io
import sqlite3
import typing as t

import numpy as np

DB_NAME = "tracker.db"


def adapt_array(arr):
    out = io.BytesIO()
    np.save(out, arr)  # type: ignore
    out.seek(0)
    return sqlite3.Binary(out.read())


def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)


def create_connection() -> sqlite3.Connection:
    try:
        conn = sqlite3.connect(DB_NAME)
    except sqlite3.Error as e:
        print(e)
        exit()
    return conn


def _register_adapter_and_converter():
    sqlite3.register_adapter(np.ndarray, adapt_array)
    sqlite3.register_converter("array", convert_array)


def _do_query(sql_query: str, values: t.Optional[tuple] = None):
    connection = create_connection()
    try:
        with contextlib.closing(connection):
            if values:
                # this means we're setting some info into the db
                connection.execute(sql_query, values)
                connection.commit()
            else:
                connection.execute(sql_query)
    except sqlite3.Error as e:
        print(e)


def create_db_table():
    _register_adapter_and_converter()

    sql_query = """CREATE TABLE IF NOT EXISTS screenshots (
                                        id integer PRIMARY KEY,
                                        coordinates_x INTEGER NOT NULL,
                                        coordinates_y INTEGER NOT NULL,
                                        image_data array NOT NULL
                                    );"""
    _do_query(sql_query)


def insert_values_into_table(coordinates_x: int, coordinates_y: int, image_data: np.ndarray):
    sql_query = """INSERT INTO screenshots(coordinates_x, coordinates_y, image_data) VALUES(?, ?, ?)"""
    _do_query(sql_query, (coordinates_x, coordinates_y, image_data))


__all__ = ["create_db_table", "insert_values_into_table"]
