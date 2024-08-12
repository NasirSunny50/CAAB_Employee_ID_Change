import pyodbc
import pandas as pd

# Database connection details
DRIVER = 'ODBC Driver 17 for SQL Server'
SERVER_NAME = '172.16.200.101'
DATABASE_NAME = 'CAAB_AFS_DB'
USER = 'sa'
PW = 'tigerCaab12#'

# Establish a connection to the database
conn_str = f"DRIVER={{{DRIVER}}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};UID={USER};PWD={PW}"
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Query to find all tables with EmployeeId column
query_tables = """
SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE COLUMN_NAME = 'EmployeeId'
"""

# Execute the query and fetch all table names
cursor.execute(query_tables)
tables = cursor.fetchall()

# Search for the specific EmployeeId in each table
employee_id = '2015220205'
tables_with_employee_id = []

for table in tables:
    table_name = table[0]
    query_search = f"SELECT 1 FROM {table_name} WHERE EmployeeId = ?"
    cursor.execute(query_search, employee_id)
    if cursor.fetchone():  # If a row is returned, the EmployeeId exists in this table
        tables_with_employee_id.append(table_name)

# Print the tables that contain the specific EmployeeId
print("Database tables containing EmployeeId: " + employee_id +"")
for table_name in tables_with_employee_id:
    print(table_name)

# Close the database connection
cursor.close()
conn.close()
