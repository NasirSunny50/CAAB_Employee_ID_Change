import pyodbc
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Testbed Database connection details
# DRIVER = 'ODBC Driver 17 for SQL Server'
# SERVER_NAME = '172.16.200.101'
# DATABASE_NAME = 'CAAB_AFS_DB'
# USER = 'sa'
# PW = 'tigerCaab12#'



# Database connection details
DRIVER = 'ODBC Driver 17 for SQL Server'
SERVER_NAME = '172.16.160.21'
DATABASE_NAME = 'CAAB_AFS_DB'
USER = 'sa'
PW = '@skyDB#96$caab'

def check_foreign_keys_status():
    try:
        # Establish a connection to the database
        conn_str = f"DRIVER={{{DRIVER}}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};UID={USER};PWD={PW}"
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        logging.info("Connected to the database.")

        # Query to check the status of foreign key constraints
        query = """
        SELECT 
            fk.name AS ForeignKeyName,
            OBJECT_NAME(fk.parent_object_id) AS TableName,
            fk.is_disabled AS IsDisabled
        FROM sys.foreign_keys AS fk;
        """
        cursor.execute(query)
        foreign_keys = cursor.fetchall()

        # Print the status of each foreign key constraint
        logging.info("Foreign key constraints status:")
        for fk in foreign_keys:
            status = "Enabled" if fk.IsDisabled == 0 else "Disabled"
            logging.info(f"Foreign Key: {fk.ForeignKeyName}, Table: {fk.TableName}, Status: {status}")

        # Close the database connection
        cursor.close()
        conn.close()
        logging.info("Database connection closed.")

    except Exception as e:
        logging.error("Error occurred: %s", str(e))

if __name__ == "__main__":
    check_foreign_keys_status()
