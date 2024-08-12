import pyodbc
import tkinter as tk
from tkinter import messagebox
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Production Database connection details
DRIVER = 'ODBC Driver 17 for SQL Server'
SERVER_NAME = '172.16.160.21'
DATABASE_NAME = 'CAAB_AFS_DB'
USER = 'sa'
PW = '@skyDB#96$caab'

# Function to disable all foreign key constraints
def disable_foreign_keys(cursor):
    logging.info("Disabling foreign key constraints.")
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
    logging.info("Foreign key constraints disabled.")

# Function to enable all foreign key constraints
def enable_foreign_keys(cursor):
    logging.info("Enabling foreign key constraints.")
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
    logging.info("Foreign key constraints enabled.")

def swap_employee_ids(present_employee_id, new_employee_id, result_text):
    try:
        logging.info("Starting the employee ID swap process.")
        
        # Establish a connection to the database
        conn_str = f"DRIVER={{{DRIVER}}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};UID={USER};PWD={PW}"
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        logging.info("Connected to the database.")

        # Disable foreign key constraints
        disable_foreign_keys(cursor)

        # Query to find all tables with EmployeeId column
        query_tables = """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE COLUMN_NAME = 'EmployeeId'
        """
        cursor.execute(query_tables)
        tables = cursor.fetchall()
        logging.info(f"Found {len(tables)} tables with EmployeeId column.")

        impacted_tables = []

        # Update the EmployeeId in each table
        for table in tables:
            table_name = table[0]
            logging.info(f"Checking table: {table_name}")

            query_check = f"SELECT 1 FROM {table_name} WHERE EmployeeId = ?"
            cursor.execute(query_check, present_employee_id)
            if cursor.fetchone():  # If a row is returned, the EmployeeId exists in this table
                logging.info(f"EmployeeId {present_employee_id} found in {table_name}. Updating to {new_employee_id}.")
                
                query_update = f"UPDATE {table_name} SET EmployeeId = ? WHERE EmployeeId = ?"
                cursor.execute(query_update, new_employee_id, present_employee_id)
                impacted_tables.append(table_name)

        # Commit the changes to the database
        conn.commit()
        logging.info("Database changes committed.")

        # Enable foreign key constraints
        enable_foreign_keys(cursor)

        # Close the database connection
        cursor.close()
        conn.close()
        logging.info("Database connection closed.")

        # Update the result_text widget with the impacted tables
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Updated EmployeeId in the following tables:\n")
        result_text.insert(tk.END, "\n".join(impacted_tables))
        result_text.config(state=tk.DISABLED)

        messagebox.showinfo("Success", "Employee IDs swapped successfully!")
        logging.info("Employee ID swap process completed successfully.")

    except Exception as e:
        messagebox.showerror("Error", str(e))
        logging.error("Error occurred: %s", str(e))

def create_gui():
    root = tk.Tk()
    root.title("Employee ID Swap")

    tk.Label(root, text="Present Employee ID:").grid(row=0, column=0, padx=10, pady=5)
    present_id_entry = tk.Entry(root)
    present_id_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="New Employee ID:").grid(row=1, column=0, padx=10, pady=5)
    new_id_entry = tk.Entry(root)
    new_id_entry.grid(row=1, column=1, padx=10, pady=5)

    result_text = tk.Text(root, height=10, width=50, state=tk.DISABLED)
    result_text.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def on_swap_button_click():
        present_employee_id = present_id_entry.get()
        new_employee_id = new_id_entry.get()
        if not present_employee_id or not new_employee_id:
            messagebox.showerror("Input Error", "Please enter both Employee IDs.")
            logging.warning("Input error: One or both Employee IDs are missing.")
            return
        swap_employee_ids(present_employee_id, new_employee_id, result_text)

    swap_button = tk.Button(root, text="Swap", command=on_swap_button_click)
    swap_button.grid(row=2, column=0, columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
