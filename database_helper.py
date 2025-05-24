import mysql.connector
import xml.etree.ElementTree as ET

class DatabaseHelper:
    def __init__(self, host="localhost", user="root", password="", db_name="my_data"):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()
        self.db_name = db_name
        self.setup_database()

    def setup_database(self):
        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
        self.conn.database = self.db_name
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(30),
                age INT,
                department VARCHAR(30),
                salary INT,
                city VARCHAR(30)
            )
        """)
        self.conn.commit()

    def insert_record(self, name, age, department, salary, city):
        self.cursor.execute("""
            INSERT INTO employees (name, age, department, salary, city)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, age, department, salary, city))
        self.conn.commit()

    def fetch_all(self):
        self.cursor.execute("SELECT * FROM employees")
        return self.cursor.fetchall()

    def update_record(self, emp_id, name, age, department, salary, city):
        self.cursor.execute("""
            UPDATE employees SET name=%s, age=%s, department=%s, salary=%s, city=%s WHERE id=%s
        """, (name, age, department, salary, city, emp_id))
        self.conn.commit()

    def delete_record(self, emp_id):
        self.cursor.execute("DELETE FROM employees WHERE id=%s", (emp_id,))
        self.conn.commit()

    def export_to_xml(self, filepath="employees.xml"):
        data = self.fetch_all()
        root = ET.Element("Employees")
        for emp in data:
            emp_elem = ET.SubElement(root, "Employee", id=str(emp[0]))
            ET.SubElement(emp_elem, "Name").text = emp[1]
            ET.SubElement(emp_elem, "Age").text = str(emp[2])
            ET.SubElement(emp_elem, "Department").text = emp[3]
            ET.SubElement(emp_elem, "Salary").text = str(emp[4])
            ET.SubElement(emp_elem, "City").text = emp[5]
        tree = ET.ElementTree(root)
        tree.write(filepath)

    def close(self):
        self.cursor.close()
        self.conn.close()
