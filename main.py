import numpy as np
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
from js import document, setTimeout
from pyodide.ffi import create_proxy


# Matplotlib setup for PyScript
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
from pyscript import display

students = []

class Student:
    def __init__(self, sid, name, age, course, marks):
        self.sid = sid
        self.name = name
        self.age = age
        self.course = course
        self.marks = marks
        self.average = sum(marks) / len(marks)
        self.grade = self.calculate_grade()

    def calculate_grade(self):
        avg = self.average
        if avg >= 90: return 'A+'
        elif avg >= 80: return 'A'
        elif avg >= 70: return 'B'
        elif avg >= 60: return 'C'
        elif avg >= 50: return 'D'
        else: return 'F'

    def display(self):
        return f"ID: {self.sid:5} | Name: {self.name:15} | Age: {self.age:2} | Course: {self.course:10} | Avg: {self.average:5.1f} | Grade: {self.grade}"

def print_out(text): 
    document.getElementById('output').innerText = str(text)

def clear_plot():
    document.getElementById('plot').innerHTML = ""

def register_student(event):
    try:
        sid = document.getElementById('sid').value.strip()
        name = document.getElementById('name').value.strip()
        age = int(document.getElementById('age').value)
        course = document.getElementById('course').value.strip()
        marks = [float(m.strip()) for m in document.getElementById('marks').value.split(',')]
        if age < 10 or age > 100: raise ValueError("Age must be between 10-100")
        if any(char.isdigit() for char in course): raise ValueError("Course should not contain numbers")
        if not all(0 <= m <= 100 for m in marks): raise ValueError("Marks must be 0-100")
        if not all([sid, name, course]): raise ValueError("All fields required")
        if len(marks) != 3: raise ValueError("Enter exactly 3 marks")
        if any(s.sid == sid for s in students): raise ValueError("Student ID exists")

        student = Student(sid, name, age, course, marks)
        students.append(student)
        print_out(f"✓ SUCCESS: Student Registered\n\n{student.display()}\n\nTotal Students: {len(students)}")
        clear_plot()
        
        for id in ['sid', 'name', 'age', 'course', 'marks']:
            document.getElementById(id).value = ""
    except Exception as e:
        print_out(f"✗ ERROR: {str(e)}")

def display_students(event):
    clear_plot()
    if not students:
        print_out("No student records found. Register a student first.")
    else:
        result = f"ALL STUDENT RECORDS ({len(students)} Total)\n\n"
        for i, s in enumerate(students, 1): 
            result += f"{i}. {s.display()}\n"
        print_out(result)

def sort_students(event):
    clear_plot()
    if not students:
        print_out("No students to sort.")
        return
    students.sort(key=lambda x: x.name.lower())
    result = f"SORTED BY NAME\n\n"
    for i, s in enumerate(students, 1): 
        result += f"{i}. {s.display()}\n"
    print_out(result)

def numpy_analysis(event):
    clear_plot()
    if not students:
        print_out("No data for analysis. Register students first.")
        return
    avgs = np.array([s.average for s in students])
    result = f"NUMPY STATISTICAL ANALYSIS\n\n"
    result += f"Count Of Students:   {len(avgs)}\n"
    result += f"Mean of Marks:       {np.mean(avgs):.2f}\n"
    result += f"Median Of Marks:     {np.median(avgs):.2f}\n"
    result += f"Maximum Marks:       {np.max(avgs):.2f}\n"
    result += f"Minimum Marks:       {np.min(avgs):.2f}\n"
    result += f"Standard deviation:  {np.std(avgs):.2f}\n"
    result += f"Variance:            {np.var(avgs):.2f}"
    print_out(result)
def pandas_analysis(event):
    clear_plot()
    if not students:
        print_out("No data for analysis. Register students first.")
        return
    
    # Create dataframe with only Name and Grade
    df = pd.DataFrame({
        'Name': [s.name for s in students],
        'Grade': [s.grade for s in students]
    })
    
    result = f"STUDENT GRADES - PANDAS\n{'-'*25}\n"
    result += f"{df.to_string(index=False)}\n"
    result += f"{'-'*25}\n\n"
    
    print_out(result)

def plot_grades(event):
    if not students:
        print_out("No data to plot. Register students first.")
        return
    
    clear_plot()
    
    # Data prep
    names = [s.name for s in students]
    averages = [s.average for s in students]
    colors = ['#2ecc71' if avg >= 80 else '#f39c12' if avg >= 60 else '#e74c3c' for avg in averages]
    
    # Create plot
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(names, averages, color=colors)
    ax.set_ylabel('Average Marks', fontsize=12)
    ax.set_xlabel('Student Name', fontsize=12)
    ax.set_title('Student Performance Dashboard', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.axhline(y=60, color='r', linestyle='--', alpha=0.3, label='Pass Mark')
    ax.bar_label(bars, fmt='%.1f', padding=3)
    ax.legend()
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Render to page
    display(fig, target="plot")
    print_out(f"✓ Plotted {len(students)} students. Green=80+, Orange=60+, Red=<60")

def init():
    # Bind all 6 buttons
    document.getElementById('register_btn').addEventListener('click', create_proxy(register_student))
    document.getElementById('display_btn').addEventListener('click', create_proxy(display_students))
    document.getElementById('sort_btn').addEventListener('click', create_proxy(sort_students))
    document.getElementById('numpy_btn').addEventListener('click', create_proxy(numpy_analysis))
    document.getElementById('pandas_btn').addEventListener('click', create_proxy(pandas_analysis))
    document.getElementById('plot_btn').addEventListener('click', create_proxy(plot_grades))
    print_out("Smart Campus Portal Ready\n\nEnter student details and click Register")

setTimeout(create_proxy(init), 300)