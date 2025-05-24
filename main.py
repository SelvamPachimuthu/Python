import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
import re
import sys

from System.Windows.Forms import (
    Application, Label, TextBox, Button, Form,
    DataGridView, DataGridViewTextBoxColumn, MessageBox
)
from System.Drawing import Point, Size

# Import your helper
from database_helper import DatabaseHelper  # Change to correct module/file name

class MyForm(Form):
    def __init__(self):
        super(MyForm, self).__init__()
        self.Text = 'Employee Record - CRUD  with Validation'
        self.Size = Size(720, 530)

        self.db = DatabaseHelper(host="localhost", user="root", password="", db_name="my_data")

        labels = ["Name", "Age", "Department", "Salary", "City"]
        self.textboxes = {}

        for i, field in enumerate(labels):
            lbl = Label()
            lbl.Text = field
            lbl.Location = Point(10 + i * 130, 10)
            self.Controls.Add(lbl)

            txt = TextBox()
            txt.Location = Point(10 + i * 130, 30)
            txt.Size = Size(120, 20)
            self.Controls.Add(txt)

            self.textboxes[field.lower()] = txt

        # Buttons
        self.btn_add = Button()
        self.btn_add.Text = "Create"
        self.btn_add.Location = Point(10, 60)
        self.btn_add.Click += self.create_record
        self.Controls.Add(self.btn_add)

        self.btn_update = Button()
        self.btn_update.Text = "Update"
        self.btn_update.Location = Point(100, 60)
        self.btn_update.Click += self.update_record
        self.Controls.Add(self.btn_update)

        self.btn_delete = Button()
        self.btn_delete.Text = "Delete"
        self.btn_delete.Location = Point(190, 60)
        self.btn_delete.Click += self.delete_record
        self.Controls.Add(self.btn_delete)

        self.btn_clear = Button()
        self.btn_clear.Text = "Clear"
        self.btn_clear.Location = Point(280, 60)
        self.btn_clear.Click += self.clear_textboxes
        self.Controls.Add(self.btn_clear)

        self.btn_read = Button()
        self.btn_read.Text = "Read"
        self.btn_read.Location = Point(370, 60)
        self.btn_read.Click += self.read_record
        self.Controls.Add(self.btn_read)

        # Grid
        self.grid = DataGridView()
        self.grid.Location = Point(10, 100)
        self.grid.Size = Size(680, 370)
        self.grid.AllowUserToAddRows = False
        self.grid.ReadOnly = False
        self.grid.SelectionMode = self.grid.SelectionMode.FullRowSelect
        self.grid.Click += self.fill_textboxes

        # Columns (ID used for primary key)
        self.grid.Columns.Add(self.make_column("ID", 50))
        self.grid.Columns.Add(self.make_column("Name", 100))
        self.grid.Columns.Add(self.make_column("Age", 60))
        self.grid.Columns.Add(self.make_column("Department", 120))
        self.grid.Columns.Add(self.make_column("Salary", 100))
        self.grid.Columns.Add(self.make_column("City", 100))

        self.Controls.Add(self.grid)

        # Load existing records from DB
        self.load_from_database()

    def make_column(self, header, width):
        col = DataGridViewTextBoxColumn()
        col.HeaderText = header
        col.Width = width
        return col

    def is_valid_input(self):
        name = self.textboxes["name"].Text.strip()
        age = self.textboxes["age"].Text.strip()
        dept = self.textboxes["department"].Text.strip()
        salary = self.textboxes["salary"].Text.strip()
        city = self.textboxes["city"].Text.strip()

        if not re.match(r"^[A-Za-z ]{1,30}$", name):
            MessageBox.Show("Invalid Name. Only letters, max 30 characters.")
            return False
        if not age.isdigit() or not (0 <= int(age) <= 100):
            MessageBox.Show("Invalid Age. Enter a number between 0 and 100.")
            return False
        if not re.match(r"^[A-Za-z ]{1,30}$", dept):
            MessageBox.Show("Invalid Department. Only letters, max 30 characters.")
            return False
        if not salary.isdigit():
            MessageBox.Show("Invalid Salary. Only numbers allowed.")
            return False
        if not re.match(r"^[A-Za-z ]{1,30}$", city):
            MessageBox.Show("Invalid City. Only letters, max 30 characters.")
            return False

        return True

    def get_inputs(self):
        return [
            self.textboxes["name"].Text.strip(),
            self.textboxes["age"].Text.strip(),
            self.textboxes["department"].Text.strip(),
            self.textboxes["salary"].Text.strip(),
            self.textboxes["city"].Text.strip()
        ]

    def create_record(self, sender, event):
        if self.is_valid_input():
            values = self.get_inputs()
            self.db.insert_record(*values)
            self.load_from_database()
            self.clear_textboxes(None, None)

    def update_record(self, sender, event):
        if self.grid.SelectedRows.Count > 0 and self.is_valid_input():
            row = self.grid.SelectedRows[0]
            emp_id = int(row.Cells[0].Value)
            values = self.get_inputs()
            self.db.update_record(emp_id, *values)
            self.load_from_database()
            self.clear_textboxes(None, None)
        else:
            MessageBox.Show("Please select a row to update.")

    def delete_record(self, sender, event):
        if self.grid.SelectedRows.Count > 0:
            row = self.grid.SelectedRows[0]
            emp_id = int(row.Cells[0].Value)
            self.db.delete_record(emp_id)
            self.load_from_database()
            self.clear_textboxes(None, None)
        else:
            MessageBox.Show("Please select a row to delete.")

    def load_from_database(self):
        self.grid.Rows.Clear()
        records = self.db.fetch_all()
        for emp in records:
            self.grid.Rows.Add([str(emp[0])] + list(map(str, emp[1:])))

    def fill_textboxes(self, sender, event):
        self.read_selected_row()

    def read_record(self, sender, event):
        self.read_selected_row()

    def read_selected_row(self):
        if self.grid.SelectedRows.Count > 0:
            row = self.grid.SelectedRows[0]
            self.textboxes["name"].Text = row.Cells[1].Value
            self.textboxes["age"].Text = row.Cells[2].Value
            self.textboxes["department"].Text = row.Cells[3].Value
            self.textboxes["salary"].Text = row.Cells[4].Value
            self.textboxes["city"].Text = row.Cells[5].Value
        else:
            MessageBox.Show("Please select a row to read.")

    def clear_textboxes(self, sender, event):
        for tb in self.textboxes.values():
            tb.Text = ""

# Start the form
form = MyForm()
Application.Run(form)
