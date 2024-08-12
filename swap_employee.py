import pyodbc

# Database connection details
DRIVER = 'ODBC Driver 17 for SQL Server'
SERVER_NAME = '192.168.104.101'
DATABASE_NAME = 'CAAB_AFS_DB'
USER = 'sa'
PW = 'Tigerit12#'

# Employee IDs
present_employee_id = '1111111111'
new_employee_id = '2024330005'

# Establish a connection to the database
conn_str = f"DRIVER={{{DRIVER}}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};UID={USER};PWD={PW}"
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Function to disable all foreign key constraints
def disable_foreign_keys(cursor):
    cursor.execute("""
    DECLARE @sql NVARCHAR(MAX) = N'';
    SELECT @sql += 'ALTER TABLE ' + QUOTENAME(s.name) + '.' + QUOTENAME(t.name) + 
                   ' NOCHECK CONSTRAINT ' + QUOTENAME(c.name) + ';' + CHAR(13)
    FROM sys.foreign_keys AS c
    INNER JOIN sys.tables AS t ON c.parent_object_id = t.object_id
    INNER JOIN sys.schemas AS s ON t.schema_id = s.schema_id;
    EXEC sp_executesql @sql;
    """)
    cursor.commit()

# Function to enable all foreign key constraints
def enable_foreign_keys(cursor):
    cursor.execute("""
    DECLARE @sql NVARCHAR(MAX) = N'';
    SELECT @sql += 'ALTER TABLE ' + QUOTENAME(s.name) + '.' + QUOTENAME(t.name) + 
                   ' CHECK CONSTRAINT ' + QUOTENAME(c.name) + ';' + CHAR(13)
    FROM sys.foreign_keys AS c
    INNER JOIN sys.tables AS t ON c.parent_object_id = t.object_id
    INNER JOIN sys.schemas AS s ON t.schema_id = s.schema_id;
    EXEC sp_executesql @sql;
    """)
    cursor.commit()

# Disable foreign key constraints
disable_foreign_keys(cursor)

# Query to find all tables with EmployeeId column
query_tables = """
SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE COLUMN_NAME = 'EmployeeId'
"""

# Execute the query and fetch all table names
cursor.execute(query_tables)
tables = cursor.fetchall()

# Update the EmployeeId in each table
for table in tables:
    table_name = table[0]
    # Check if the present_employee_id exists in the table
    query_check = f"SELECT 1 FROM {table_name} WHERE EmployeeId = ?"
    cursor.execute(query_check, present_employee_id)
    if cursor.fetchone():  # If a row is returned, the EmployeeId exists in this table
        # Update the EmployeeId
        query_update = f"UPDATE {table_name} SET EmployeeId = ? WHERE EmployeeId = ?"
        cursor.execute(query_update, new_employee_id, present_employee_id)
        print(f"Updated EmployeeId in table: {table_name}")

# Commit the changes to the database
conn.commit()

# Enable foreign key constraints
enable_foreign_keys(cursor)

# Close the database connection
cursor.close()
conn.close()
