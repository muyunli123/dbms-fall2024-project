# db_utils.py
import pyodbc as odbc

def get_db_connection():
    """
    Establish a connection to the database using a connection string.
    Update the connection string with your database details.
    """
    connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:carrentalfords.database.windows.net,1433;Database=CarRental;Uid=carrental;Pwd={1987@Fjkl};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    conn = odbc.connect(connection_string)
    return conn
