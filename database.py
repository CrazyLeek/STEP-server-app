import sqlite3

def connect_to_db():
    """
    SQLite Database Connection

    This module establishes a connection to an SQLite database using the 'sqlite3' interface.

    Functions :
    - connect_to_db(): Establishes a connection to the database

    Dependencies :
    - sqlite3: Python interface for sqlite.
    """
    try:
        con = sqlite3.connect('../../db/step-db/stepdb.db')
        return con
    except sqlite3.Error as er:
        raise Exception(f"Failed to connect to the database. Error code : {er.sqlite_errorcode} Error message : {er.sqlite_errorname}")