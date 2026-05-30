from pyscript import document, when, display
from js import console, Blob, URL, document as jsdoc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
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
def calculate_fee(tuition_fee, lab_fee=2000, transport_fee=1000):
    return tuition_fee + lab_fee + transport_fee

def fee_handler(event):
    document.querySelector("#output").innerHTML = ""
    try:
        tuition_str = get_val("tuition_fee").strip()
        if not tuition_str:
            raise ValueError("Tuition fee cannot be empty")
        tuition = float(tuition_str)
        if tuition <= 0:
            raise ValueError("Tuition fee must be positive")
        total_fee = calculate_fee(tuition)
        print_output(f"=== Fee Calculation ===\nTuition Fee: ₹{tuition}\nLab Fee: ₹2000\nTransport Fee: ₹1000\n{'-'*25}\nTotal Fee: ₹{total_fee}")
    except ValueError as e:
        print_output(f"Invalid input! {e}", is_error=True)

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

# ---------------- EXCEPTION DEMO ----------------
def exception_demo(event):
    document.querySelector("#output").innerHTML = ""
    try:
        demo_type = get_val("sid").strip()
        if demo_type == "1":
            raise InvalidStudentError("This is a custom InvalidStudentError")
        elif demo_type == "2":
            int("abc") # ValueError
        elif demo_type == "3":
            x = 10 / 0 # ZeroDivisionError
        else:
            result = "=== Exception Handling Demo ===\n"
            result += "Enter 1 in Student ID for InvalidStudentError\n"
            result += "Enter 2 for ValueError\n"
            result += "Enter 3 for ZeroDivisionError"
            print_output(result)
            return
    except InvalidStudentError as e:
        print_output(f"Caught Custom Exception:\n{e}", is_error=True)
    except ValueError as e:
        print_output(f"Caught ValueError:\n{e}", is_error=True)
    except ZeroDivisionError as e:
        print_output(f"Caught ZeroDivisionError:\n{e}", is_error=True)
    except Exception as e:
        print_output(f"Caught General Exception:\n{e}", is_error=True)

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
def _6(e): fee_handler(e)
@when("click", "#save_btn")
def _ex(e): exception_demo(e)
@when("click", "#numpy_btn")
def _11(e): numpy_analysis(e)
@when("click", "#pandas_btn")
def _12(e): pandas_analysis(e)
@when("click", "#plot_btn")
def _13(e): visualize_data(e)

print_output("Ready! All modules loaded with exception handling.\nEnter data and test.")