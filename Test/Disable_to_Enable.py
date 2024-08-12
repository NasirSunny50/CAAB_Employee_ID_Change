import pyodbc
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection details
DRIVER = 'ODBC Driver 17 for SQL Server'
SERVER_NAME = '172.16.160.21'
DATABASE_NAME = 'CAAB_AFS_DB'
USER = 'sa'
PW = '@skyDB#96$caab'

def find_and_enable_disabled_foreign_keys():
    try:
        # Establish a connection to the database
        conn_str = f"DRIVER={{{DRIVER}}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};UID={USER};PWD={PW}"
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        logging.info("Connected to the database.")

        # Query to find disabled foreign key constraints
        query_disabled_keys = """
        SELECT 
            fk.name AS ForeignKeyName,
            OBJECT_NAME(fk.parent_object_id) AS TableName
        FROM sys.foreign_keys AS fk
        WHERE fk.is_disabled = 1;
        """
        cursor.execute(query_disabled_keys)
        disabled_keys = cursor.fetchall()

        if not disabled_keys:
            logging.info("No disabled foreign keys found.")
        else:
            # Enable foreign keys in batches
            batch_size = 10  # Adjust batch size as needed
            for i in range(0, len(disabled_keys), batch_size):
                batch = disabled_keys[i:i + batch_size]
                for fk in batch:
                    logging.info(f"Enabling Foreign Key: {fk.ForeignKeyName} on Table: {fk.TableName}")
                    enable_query = f"ALTER TABLE {fk.TableName} WITH CHECK CHECK CONSTRAINT {fk.ForeignKeyName};"
                    cursor.execute(enable_query)
                    conn.commit()

            logging.info("Enabled all disabled foreign keys.")

        # Close the database connection
        cursor.close()
        conn.close()
        logging.info("Database connection closed.")

    except Exception as e:
        logging.error("Error occurred: %s", str(e))

if __name__ == "__main__":
    find_and_enable_disabled_foreign_keys()
