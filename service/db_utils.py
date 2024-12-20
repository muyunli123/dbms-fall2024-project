# db_utils.py
import pyodbc as odbc

def get_db_connection():
    """
    Establish a connection to the database using a connection string.
    Update the connection string with your database details.
    """
    connection_string = ""
    conn = odbc.connect(connection_string)
    return conn
