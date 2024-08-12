import pyodbc
import tkinter as tk
from tkinter import messagebox

# Testbed Database connection details
# DRIVER = 'ODBC Driver 17 for SQL Server'
# SERVER_NAME = '172.16.200.101'
# DATABASE_NAME = 'CAAB_AFS_DB'
# USER = 'sa'
# PW = 'tigerCaab12#'

# Production Database connection details
DRIVER = 'ODBC Driver 17 for SQL Server'
SERVER_NAME = '172.16.160.21'
DATABASE_NAME = 'CAAB_AFS_DB'
USER = 'sa'
PW = '@skyDB#96$caab'


def search_employee_id(employee_id, result_text):
    try:
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

        tables_with_employee_id = []

        # Search for the specific EmployeeId in each table
        for table in tables:
            table_name = table[0]
            query_search = f"SELECT 1 FROM {table_name} WHERE EmployeeId = ?"
            cursor.execute(query_search, employee_id)
            if cursor.fetchone():  # If a row is returned, the EmployeeId exists in this table
                tables_with_employee_id.append(table_name)

        # Close the database connection
        cursor.close()
        conn.close()

        # Update the result_text widget with the tables containing the EmployeeId
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        if tables_with_employee_id:
            result_text.insert(tk.END, f"Database tables containing EmployeeId {employee_id}:\n")
            result_text.insert(tk.END, "\n".join(tables_with_employee_id))
        else:
            result_text.insert(tk.END, f"No tables contain EmployeeId {employee_id}.")
        result_text.config(state=tk.DISABLED)

    except Exception as e:
        messagebox.showerror("Error", str(e))

def create_gui():
    root = tk.Tk()
    root.title("Employee ID Search")

    tk.Label(root, text="Employee ID:").grid(row=0, column=0, padx=10, pady=5)
    employee_id_entry = tk.Entry(root)
    employee_id_entry.grid(row=0, column=1, padx=10, pady=5)

    result_text = tk.Text(root, height=10, width=50, state=tk.DISABLED)
    result_text.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def on_search_button_click():
        employee_id = employee_id_entry.get()
        if not employee_id:
            messagebox.showerror("Input Error", "Please enter an Employee ID.")
            return
        search_employee_id(employee_id, result_text)

    search_button = tk.Button(root, text="Search", command=on_search_button_click)
    search_button.grid(row=1, column=0, columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
