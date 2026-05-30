from pyscript import when, display
from js import document, console
from pyodide.ffi import create_proxy
import csv
import io
from js import Blob, URL, document
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("agg")
import json

matplotlib.use("agg")

# ---------------- GLOBAL VARIABLES ----------------
students = []

# ---------------- USER DEFINED EXCEPTION ----------------
class InvalidStudentError(Exception):
    pass

# ---------------- STUDENT CLASS ----------------
class Student:
    def __init__(self, sid, name, age, course, marks):
        self.sid = sid
        self.name = name
        self.age = age
        self.course = course
        self.marks = marks
        self.grade = self.calculate_grade()

    def calculate_grade(self):
        average = sum(self.marks) / len(self.marks)
        if average >= 90: return 'A+'
        elif average >= 80: return 'A'
        elif average >= 70: return 'B'
        elif average >= 60: return 'C'
        elif average >= 50: return 'D'
        else: return 'F'

    def display(self):
        return f"\nStudent ID: {self.sid}\nName: {self.name}\nAge: {self.age}\nCourse: {self.course}\nMarks: {self.marks}\nGrade: {self.grade}"

    def to_dict(self):
        return {'ID': self.sid, 'Name': self.name, 'Age': self.age, 'Course': self.course, 'Marks': self.marks, 'Grade': self.grade}

# ---------------- HELPER FUNCTIONS ----------------
    


def generate_csv_report(e=None):
    try:
        out = document.getElementById("output")
        
        if not students:
            out.innerText = "❌ No students registered. Add students first."
            return
            
        FEE_STRUCTURE = {
            'BCA': 50000, 'BCOM': 45000, 'BBA': 55000, 
            'BSC': 40000, 'OTHER': 35000
        }
        
        # Create CSV in memory instead of file
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Name', 'Age', 'Course', 'Grade', 'Average_Marks', 'Fee'])
        
        for s in students:
            avg = sum(s.marks) / len(s.marks)
            course_key = s.course.upper()
            fee = FEE_STRUCTURE.get('BCA') if 'BCA' in course_key else \
                  FEE_STRUCTURE.get('BCOM') if 'BCOM' in course_key else \
                  FEE_STRUCTURE.get('BBA') if 'BBA' in course_key else \
                  FEE_STRUCTURE.get('BSC') if 'BSC' in course_key else \
                  FEE_STRUCTURE.get('OTHER')
                  
            writer.writerow([s.sid, s.name, s.age, s.course, s.grade, round(avg,2), fee])
        
        # Create download link
        csv_content = output.getvalue()
        blob = Blob.new([csv_content], {"type": "text/csv"})
        url = URL.createObjectURL(blob)
        
        link = document.getElementById("download_link")
        link.href = url
        link.download = "student_report.csv"
        link.click()  # Auto-download
        
        out.innerText = f"✅ CSV report generated! Downloaded {len(students)} records."
        
    except Exception as err:
        document.getElementById("output").innerText = f"ERROR: {err}"
        console.log(str(err))

# ------------------ BUTTON BINDINGS ------------------
@when("click", "#csv_btn")
def _7(e): generate_csv_report(e)
def print_output(text, is_error=False):
    cls = "error" if is_error else ""
    document.querySelector("#output").innerHTML = f"<pre class='{cls}'>{text}</pre>"

def get_val(id):
    return document.querySelector(f"#{id}").value

def set_val(id, val):
    document.querySelector(f"#{id}").value = val

def hide_all_modes():
    document.querySelector("#normal_mode").style.display = "none"
    document.querySelector("#search_mode").style.display = "none"
    document.querySelector("#update_mode").style.display = "none"

def show_normal_mode():
    hide_all_modes()
    document.querySelector("#normal_mode").style.display = "block"

def download_file(filename, content):
    blob = Blob.new([content], {type: "application/json"})
    url = URL.createObjectURL(blob)
    a = jsdoc.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)

# ---------------- 1. REGISTER WITH FULL EXCEPTION HANDLING ----------------
from js import FileReader
from pyodide.ffi import create_proxy

def scan_uploaded_files(e=None):
    out = document.getElementById("output")
    files = document.getElementById("file_input").files
    
    if files.length == 0:
        out.innerText = "❌ No files selected. Choose files first."
        return
    
    report = f"--- UPLOADED FILES: {files.length} ---\n\n"
    for i in range(files.length):
        f = files.item(i)
        report += f"File: {f.name}\n"
        report += f"Size: {f.size} bytes\n"
        report += f"Type: {f.type}\n{'-'*30}\n"
    
    out.innerText = report

def register_student(event):
    document.querySelector("#output").innerHTML = ""
    try:
        sid = get_val("sid").strip()
        name = get_val("name").strip()
        age_str = get_val("age").strip()
        course = get_val("course").strip()
        m1_str = get_val("mark1").strip()
        m2_str = get_val("mark2").strip()
        m3_str = get_val("mark3").strip()

        # Check empty fields
        if not sid: raise InvalidStudentError("Student ID cannot be empty")
        if not name: raise InvalidStudentError("Student Name cannot be empty")
        if not age_str: raise InvalidStudentError("Age cannot be empty")
        if not course: raise InvalidStudentError("Course cannot be empty")
        if not m1_str or not m2_str or not m3_str:
            raise InvalidStudentError("All 3 marks must be entered")

        age = int(age_str)
        if age <= 0 or age > 100:
            raise ValueError("Age must be between 1-100")

        marks = []
        for i, mark_str in enumerate([m1_str, m2_str, m3_str], 1):
            mark = float(mark_str)
            if mark < 0 or mark > 100:
                raise ValueError(f"Mark {i} must be between 0-100")
            marks.append(mark)

        for s in students:
            if s.sid == sid:
                raise InvalidStudentError(f"Student ID {sid} already exists")

        student = Student(sid, name, age, course, marks)
        students.append(student)

        for i in ["sid","name","age","course","mark1","mark2","mark3"]: set_val(i, "")
        print_output(f"Student Registered Successfully!\n{student.display()}")

    except InvalidStudentError as e:
        print_output(f"Custom Exception: {e}", is_error=True)
    except ValueError as e:
        print_output(f"Invalid input! {e}", is_error=True)
    except Exception as e:
        print_output(f"Error: {e}", is_error=True)

# ---------------- 2. DISPLAY ALL ----------------
def display_students(event):
    document.querySelector("#output").innerHTML = ""
    try:
        if not students:
            raise InvalidStudentError("No student records found.")
        result = "=== All Students ===\n"
        for s in students:
            result += s.display() + f"\n{'-'*30}"
        print_output(result)
    except InvalidStudentError as e:
        print_output(f"Custom Exception: {e}", is_error=True)

# ---------------- 3. SEARCH WITH POPUP ----------------
def show_search_mode(event):
    hide_all_modes()
    document.querySelector("#search_mode").style.display = "block"
    print_output("Enter Student ID to search")

def search_student(event):
    document.querySelector("#output").innerHTML = ""
    try:
        sid = get_val("search_sid").strip()
        if not sid:
            raise ValueError("Enter Student ID to Search")
        for s in students:
            if s.sid == sid:
                print_output(f"Student Found:{s.display()}")
                set_val("search_sid", "")
                show_normal_mode()
                return
        raise InvalidStudentError("Student not found!")
    except (ValueError, InvalidStudentError) as e:
        print_output(f"Error: {e}", is_error=True)
        set_val("search_sid", "")
        show_normal_mode()

# ---------------- 4. SORT ----------------
def sort_students(event):
    document.querySelector("#output").innerHTML = ""
    try:
        if not students:
            raise InvalidStudentError("No students to sort")
        sorted_students = sorted(students, key=lambda x: x.name)
        result = "=== Students Sorted by Name ===\n\n"
        for s in sorted_students:
            result += f"{s.name} - {s.sid} - {s.course} - Grade: {s.grade}\n"
        print_output(result)
    except InvalidStudentError as e:
        print_output(f"Custom Exception: {e}", is_error=True)

# ---------------- 5. UPDATE COURSE WITH POPUP ----------------
def show_update_mode(event):
    hide_all_modes()
    document.querySelector("#update_mode").style.display = "block"
    print_output("Enter ID and New Course")

def update_course_handler(event):
    document.querySelector("#output").innerHTML = ""
    try:
        sid = get_val("update_sid").strip()
        new_course = get_val("update_course").strip()
        if not sid or not new_course:
            raise ValueError("Enter Student ID and New Course Name")
        for s in students:
            if s.sid == sid:
                old = s.course
                s.course = new_course
                print_output(f"Course updated successfully!\n{s.name}\n{old} → {new_course}")
                set_val("update_sid", "")
                set_val("update_course", "")
                show_normal_mode()
                return
        raise InvalidStudentError("Student not found!")
    except (ValueError, InvalidStudentError) as e:
        print_output(f"Error: {e}", is_error=True)
        set_val("update_sid", "")
        set_val("update_course", "")
        show_normal_mode()

# ---------------- 6. FEE CALCULATION ----------------


students = [] # Make sure this global list exists at top

def calculate_fee(e=None):
    try:
        out = document.getElementById("output")
        
        if not students:
            out.innerText = "❌ No students registered yet. Add students first."
            return
        
        FEE_STRUCTURE = {
            'BCA': 50000, 'BCOM': 45000, 'BBA': 55000, 
            'BSC': 40000, 'OTHER': 35000
        }
        
        report = "--- STANDARD FEE STRUCTURE ---\n"
        for course, amount in FEE_STRUCTURE.items():
            report += f"{course:<8} : ₹{amount:,}\n"
        
        report += f"\n{'='*60}\n--- INDIVIDUAL STUDENT FEE CALCULATION ---\n\n"
        
        total = 0
        for s in students:
            course_key = s.course.upper()
            fee = FEE_STRUCTURE.get('BCA') if 'BCA' in course_key else \
                  FEE_STRUCTURE.get('BCOM') if 'BCOM' in course_key else \
                  FEE_STRUCTURE.get('BBA') if 'BBA' in course_key else \
                  FEE_STRUCTURE.get('BSC') if 'BSC' in course_key else \
                  FEE_STRUCTURE.get('OTHER')
            
            total += fee
            report += f"ID: {s.sid:<5} | Name: {s.name:<15} | Course: {s.course:<10} | Fee: ₹{fee:,}\n"
        
        report += f"\n{'='*60}\nTOTAL STUDENTS: {len(students)}\nGRAND TOTAL: ₹{total:,}\n{'='*60}"
        out.innerText = report
        
    except Exception as err:
        document.getElementById("output").innerText = f"ERROR: {err}"
        console.log(str(err))


# ---------------- 7. SAVE RECORDS ----------------
def save_to_file(event):
    document.querySelector("#output").innerHTML = ""
    try:
        if not students:
            raise InvalidStudentError("No records to save")
        data = [s.to_dict() for s in students]
        json_str = json.dumps(data, indent=4)
        download_file("students.json", json_str)
        print_output("Student records saved successfully!\nFile downloaded as students.json")
    except InvalidStudentError as e:
        print_output(f"Custom Exception: {e}", is_error=True)

def update_file_count(e=None):
    files = document.getElementById("file_input").files
    count_span = document.getElementById("file_count")
    
    if files.length == 0:
        count_span.innerText = "No files selected"
    else:
        count_span.innerText = f"{files.length} file{'s' if files.length > 1 else ''} selected"

def scan_uploaded_files(e=None):
    out = document.getElementById("output")
    files = document.getElementById("file_input").files
    
    if files.length == 0:
        out.innerText = "❌ No files selected."
        return
    
    report = f"=== DIRECTORY SCAN RESULT ===\n"
    report += f"Total Files Selected: {files.length}\n"
    report += f"{'='*40}\n\n"
    
    for i in range(files.length):
        f = files.item(i)
        size_kb = round(f.size / 1024, 2)
        report += f"📄 {f.name}\n"
        report += f"   Size: {size_kb} KB\n"
        report += f"   Type: {f.type or 'Unknown'}\n\n"
    
    out.innerText = report






# ---------------- 11. NUMPY ----------------
def numpy_analysis(event):
    document.querySelector("#output").innerHTML = ""
    try:
        if not students:
            raise InvalidStudentError("No data available for analysis.")
        all_marks = [sum(s.marks) / len(s.marks) for s in students]
        marks_array = np.array(all_marks)
        result = "=== NumPy Statistical Analysis ===\n\n"
        result += f"Average Marks: {np.mean(marks_array):.2f}\n"
        result += f"Highest Marks: {np.max(marks_array):.2f}\n"
        result += f"Lowest Marks: {np.min(marks_array):.2f}\n"
        result += f"Standard Deviation: {np.std(marks_array):.2f}"
        print_output(result)
    except InvalidStudentError as e:
        print_output(f"Custom Exception: {e}", is_error=True)

# ---------------- 12. PANDAS ----------------
def pandas_analysis(event):
    document.querySelector("#output").innerHTML = ""
    try:
        if not students:
            raise InvalidStudentError("No student data available.")
        data = {
            'ID': [s.sid for s in students],
            'Name': [s.name for s in students],
            'Course': [s.course for s in students],
            'Average': [sum(s.marks) / len(s.marks) for s in students],
            'Grade': [s.grade for s in students]
        }
        df = pd.DataFrame(data)
        result = "=== Pandas DataFrame ===\n\n"
        result += df.to_string(index=False)
        result += f"\n\n=== Statistical Summary ===\n"
        result += df.describe().to_string()
        print_output(result)
    except InvalidStudentError as e:
        print_output(f"Custom Exception: {e}", is_error=True)

# ---------------- 13. MATPLOTLIB IN MODAL ----------------
def visualize_data(event):
    document.querySelector("#output").innerHTML = ""
    try:
        if len(students) < 2:
            raise InvalidStudentError("Add at least 2 students to plot")

        plt.clf()
        names = [s.name for s in students]
        averages = [sum(s.marks) / len(s.marks) for s in students]

        fig, ax = plt.subplots(figsize=(6, 3.5), dpi=100)  # Smaller size
        bars = ax.bar(names, averages, color='#4CAF50', edgecolor='black')
        ax.set_xlabel('Student Names', fontsize=10)
        ax.set_ylabel('Average Marks', fontsize=10)
        ax.set_title('Student Performance Analysis', fontsize=12, fontweight='bold')
        ax.set_ylim(0, 100)
        ax.axhline(y=np.mean(averages), color='red', linestyle='--', linewidth=1.5, label=f'Avg: {np.mean(averages):.1f}')
        ax.legend(fontsize=9)
        ax.grid(axis='y', alpha=0.3)
        ax.tick_params(axis='both', labelsize=9)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1, f'{height:.1f}', ha='center', va='bottom', fontsize=8)
        
        plt.xticks(rotation=30, ha='right')
        plt.tight_layout()
        fig.canvas.manager = None

        document.querySelector("#graph_output").innerHTML = ""
        display(fig, target="graph_output", append=False)
        document.querySelector("#graphModal").style.display = "block"

    except InvalidStudentError as e:
        print_output(f"Custom Exception: {e}", is_error=True)

# ---------------- MODAL CLOSE ----------------
@when("click", "#closeModal")
def close_modal(event):
    document.querySelector("#graphModal").style.display = "none"

# ---------------- CANCEL BUTTONS ----------------
@when("click", "#cancel_search_btn")
def cancel_search(event):
    show_normal_mode()
    print_output("Search cancelled")

@when("click", "#cancel_update_btn")
def cancel_update(event):
    show_normal_mode()
    print_output("Update cancelled")

# ---------------- BUTTON BINDINGS ----------------
@when("click", "#register_btn")
def _1(e): register_student(e)
@when("click", "#display_btn")
def _2(e): display_students(e)
@when("click", "#show_search_btn")
def _3(e): show_search_mode(e)
@when("click", "#search_now_btn")
def _3b(e): search_student(e)
@when("click", "#sort_btn")
def _4(e): sort_students(e)
@when("click", "#show_update_btn")
def _5(e): show_update_mode(e)
@when("click", "#confirm_update_btn")
def _5b(e): update_course_handler(e)
@when("click", "#fee_btn")
def _6(e): calculate_fee(e)
@when("click", "#save_btn")
@when("click", "#numpy_btn")
def _11(e): numpy_analysis(e)
@when("click", "#pandas_btn")
def _12(e): pandas_analysis(e)
@when("click", "#plot_btn")
def _13(e): visualize_data(e)
@when("click", "#csv_btn")
def _7(e): generate_csv_report(e)
@when("change", "#file_input")
def _auto_scan(e): 
    scan_uploaded_files(e)

print_output("Ready! All modules loaded with exception handling.\nEnter data and test.")